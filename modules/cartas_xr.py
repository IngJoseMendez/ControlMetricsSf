# -*- coding: utf-8 -*-
"""
Módulo: Cartas de Control X̄ – R  (Variables)
Sistema SPC – PMD y Cía S.C.A.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS, SPC_CONSTANTS, FASE_I_DATA, FASE_II_DATA
from utils.spc_utils import (compute_xbar_r, compute_control_limits_xr,
                              detect_out_of_control, parse_value, compute_arl,
                              compute_power_curve, western_electric_rules)
from utils.widgets import CollapsibleChart

MAX_SUBGROUPS = 50
MAX_N = 10


class CartasXRModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._limits_cache = None   # guardará límites calculados en Fase I
        self._build_ui()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        inst = tk.Label(self, text=(
            "Ingrese los datos de cada subgrupo (n observaciones por fila). "
            "Seleccione la fase, el tamaño de subgrupo y presione  Calcular cartas."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=900, justify='left')
        inst.pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=6, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=380, width=430)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=460)
        self._build_right(right)

    # ── Panel izquierdo ───────────────────────────────────────────────────────
    def _build_left(self, parent):
        # Wrap everything in a scrollable canvas so all controls are reachable
        scroll_canvas = tk.Canvas(parent, bg=COLORS['bg_card'], highlightthickness=0)
        left_vsb = ttk.Scrollbar(parent, orient='vertical', command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=left_vsb.set)
        left_vsb.pack(side='right', fill='y')
        scroll_canvas.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(scroll_canvas, bg=COLORS['bg_card'])
        scroll_canvas.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e: scroll_canvas.configure(
            scrollregion=scroll_canvas.bbox('all')))
        scroll_canvas.bind('<MouseWheel>', lambda e: scroll_canvas.yview_scroll(
            int(-1*(e.delta/120)), 'units'))
        parent = inner  # redirect all subsequent packs into scrollable frame

        # Cabecera
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Datos de Subgrupos', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, side='left')

        # Controles
        ctrl = tk.Frame(parent, bg=COLORS['bg_card'], pady=6)
        ctrl.pack(fill='x', padx=10)

        # Fase
        tk.Label(ctrl, text='Fase:', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).grid(row=0, column=0, sticky='e', padx=(0, 4))
        self.fase_var = tk.StringVar(value='I')
        fase_cb = ttk.Combobox(ctrl, textvariable=self.fase_var, width=20, state='readonly',
                               values=['I – Estabilización', 'II – Monitoreo'])
        fase_cb.grid(row=0, column=1, sticky='w', pady=3)
        fase_cb.bind('<<ComboboxSelected>>', self._on_fase_change)

        # Tamaño de subgrupo
        tk.Label(ctrl, text='Tamaño (n):', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).grid(row=0, column=2, sticky='e', padx=(12, 4))
        self.n_var = tk.IntVar(value=DEFAULTS['subgroup_size'])
        n_spin = ttk.Spinbox(ctrl, from_=2, to=MAX_N, textvariable=self.n_var,
                             width=5, command=self._rebuild_table)
        n_spin.bind('<Return>', lambda e: self._safe_rebuild())
        n_spin.bind('<FocusOut>', lambda e: self._safe_rebuild())
        n_spin.grid(row=0, column=3, sticky='w', pady=3)

        # Límites de control (Fase II puede usar los de Fase I)
        lim_frame = tk.LabelFrame(parent, text='Límites de Control (opcional – Fase II)',
                                  bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        lim_frame.pack(fill='x', padx=10, pady=(4, 2))

        lim_inner = tk.Frame(lim_frame, bg=COLORS['bg_card'])
        lim_inner.pack(fill='x', padx=6, pady=4)
        lim_fields = [('X̄̄ (LC):', 'lc_x'), ('LCS-X:', 'ucs_x'), ('LCI-X:', 'lci_x'),
                      ('R̄ (LC):', 'lc_r'), ('LCS-R:', 'ucs_r')]
        self.lim_entries = {}
        for i, (lbl, key) in enumerate(lim_fields):
            r, c = divmod(i, 3)
            tk.Label(lim_inner, text=lbl, font=FONTS['small'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                         row=r, column=c*2, sticky='e', padx=(6, 2), pady=2)
            e = tk.Entry(lim_inner, width=8, font=FONTS['entry'], bd=1, relief='solid')
            e.grid(row=r, column=c*2+1, sticky='w', padx=(0, 8), pady=2)
            self.lim_entries[key] = e

        # Especificaciones
        spec_frame = tk.LabelFrame(parent, text='Especificaciones del Cliente (para referencia)',
                                   bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        spec_frame.pack(fill='x', padx=10, pady=(2, 4))
        spec_inner = tk.Frame(spec_frame, bg=COLORS['bg_card'])
        spec_inner.pack(fill='x', padx=6, pady=4)
        spec_fields = [('LIE (lb):', 'lie'), ('LSE (lb):', 'lse'), ('Objetivo (lb):', 'target')]
        self.spec_entries = {}
        defaults = {'lie': DEFAULTS['lie_cliente'], 'lse': DEFAULTS['lse_cliente'],
                    'target': DEFAULTS['target']}
        for i, (lbl, key) in enumerate(spec_fields):
            tk.Label(spec_inner, text=lbl, font=FONTS['small'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                         row=0, column=i*2, sticky='e', padx=(6, 2))
            e = tk.Entry(spec_inner, width=8, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, str(defaults[key]))
            e.grid(row=0, column=i*2+1, sticky='w', padx=(0, 8))
            self.spec_entries[key] = e

        # Tabla de subgrupos
        tbl_hdr = tk.Frame(parent, bg=COLORS['primary'], pady=3)
        tbl_hdr.pack(fill='x', padx=10, pady=(4, 0))
        self._tbl_hdr_frame = tbl_hdr

        # Primero empacar los del lado derecho (tkinter los reserva primero)
        tk.Button(
            tbl_hdr, text='✕ Limpiar', command=self._clear_table,
            bg=COLORS['primary'], fg='#FFCDD2', font=FONTS['small'],
            relief='flat', bd=0, cursor='hand2', padx=8, pady=2,
            activebackground=COLORS['primary_light'], activeforeground='#FFCDD2').pack(
            side='right', padx=(0, 6))

        self._tbl_collapsed = False
        self._tbl_toggle_btn = tk.Button(
            tbl_hdr, text='▲', command=self._toggle_table,
            bg=COLORS['primary'], fg=COLORS['text_white'], font=FONTS['label_b'],
            relief='flat', bd=0, cursor='hand2', padx=6, pady=0,
            activebackground=COLORS['primary_light'], activeforeground=COLORS['text_white'])
        self._tbl_toggle_btn.pack(side='left', padx=(6, 2))

        self.tbl_title = tk.Label(tbl_hdr, text='Tabla de Subgrupos (n = 6)',
                                  font=FONTS['label_b'], bg=COLORS['primary'],
                                  fg=COLORS['text_white'])
        self.tbl_title.pack(side='left', padx=(0, 6))

        # Scrollable table area
        outer = tk.Frame(parent, bg=COLORS['border'], bd=1)
        outer.pack(fill='x', padx=10, pady=(0, 4))
        self.tbl_outer = outer

        self.canvas_tbl = tk.Canvas(outer, bg=COLORS['bg_card'], height=180, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient='vertical', command=self.canvas_tbl.yview)
        hsb = ttk.Scrollbar(outer, orient='horizontal', command=self.canvas_tbl.xview)
        self.canvas_tbl.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.canvas_tbl.pack(side='left', fill='both', expand=True)

        self.tbl_inner = tk.Frame(self.canvas_tbl, bg=COLORS['bg_card'])
        self.canvas_tbl.create_window((0, 0), window=self.tbl_inner, anchor='nw')
        self.tbl_inner.bind('<Configure>', lambda e: self.canvas_tbl.configure(
            scrollregion=self.canvas_tbl.bbox('all')))

        self._entry_cells = []   # lista de listas de Entry
        self._xbar_labels = []
        self._range_labels = []
        self._rebuild_table()

        # Botones — fila 1: acción principal + limpiar
        btn_f = tk.Frame(parent, bg=COLORS['bg_card'])
        btn_f.pack(fill='x', padx=10, pady=(4, 0))
        for txt, cmd, bg, fg in [
            ('Calcular cartas', self._run, COLORS['primary'], COLORS['text_white']),
            ('Limpiar tabla', self._clear_table, '#CFD8DC', COLORS['text']),
        ]:
            tk.Button(btn_f, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Botones — fila 2: carga de fases
        btn_f2 = tk.Frame(parent, bg=COLORS['bg_card'])
        btn_f2.pack(fill='x', padx=10, pady=(3, 4))
        for txt, cmd, bg, fg in [
            ('Cargar Fase I (estudio)', self._load_fase1, COLORS['secondary'], COLORS['text']),
            ('Cargar Fase II (estudio)', self._load_fase2, '#F57F17', COLORS['text_white']),
        ]:
            tk.Button(btn_f2, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Sección Excel
        excel_sep = tk.Frame(parent, bg=COLORS['bg_card'])
        excel_sep.pack(fill='x', padx=10, pady=(0, 8))
        tk.Frame(excel_sep, bg=COLORS['border'], height=1).pack(fill='x', pady=(0, 3))
        tk.Label(excel_sep,
                 text='📋 Excel: fila 1 = encabezados  |  filas 2+ = subgrupos (col. A opcional: N° subgrupo, cols. siguientes = X1…Xn)',
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['text_light'], wraplength=400, justify='left').pack(anchor='w')
        excel_btns = tk.Frame(excel_sep, bg=COLORS['bg_card'])
        excel_btns.pack(fill='x', pady=2)
        tk.Button(excel_btns, text='📂 Cargar desde Excel', command=self._load_excel,
                  bg='#0277BD', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)
        tk.Button(excel_btns, text='📄 Plantilla Excel', command=self._gen_template,
                  bg='#37474F', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

    def _safe_rebuild(self):
        try:
            n = self.n_var.get()
            n = max(2, min(MAX_N, n))
            self.n_var.set(n)
        except Exception:
            self.n_var.set(DEFAULTS['subgroup_size'])
        self._rebuild_table()

    def _toggle_table(self):
        if self._tbl_collapsed:
            self.tbl_outer.pack(after=self._tbl_hdr_frame, fill='x', padx=10, pady=(0, 4))
            self._tbl_toggle_btn.configure(text='▲ Reducir')
            self._tbl_collapsed = False
        else:
            self.tbl_outer.pack_forget()
            self._tbl_toggle_btn.configure(text='▼ Expandir')
            self._tbl_collapsed = True

    def _rebuild_table(self):
        n = self.n_var.get()
        self.tbl_title.configure(text=f'Tabla de Subgrupos (n = {n})')
        for w in self.tbl_inner.winfo_children():
            w.destroy()
        self._entry_cells.clear()
        self._xbar_labels.clear()
        self._range_labels.clear()

        # Encabezado
        headers = ['SG'] + [f'X{i+1}' for i in range(n)] + ['X̄', 'R']
        col_widths = [4] + [7]*n + [8, 8]
        for j, (h, w) in enumerate(zip(headers, col_widths)):
            bg = COLORS['primary'] if j == 0 else (COLORS['primary_light'] if j <= n else COLORS['bg_subheader'])
            tk.Label(self.tbl_inner, text=h, font=FONTS['label_b'], bg=bg,
                     fg=COLORS['text_white'], width=w, pady=4).grid(row=0, column=j, padx=1, pady=1, sticky='ew')

        # Filas
        for i in range(MAX_SUBGROUPS):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            tk.Label(self.tbl_inner, text=str(i+1), font=FONTS['small'],
                     bg=COLORS['primary_lighter'], fg=COLORS['text_white'], width=4).grid(
                         row=i+1, column=0, padx=1, pady=1)
            row_entries = []
            for j in range(n):
                e = tk.Entry(self.tbl_inner, width=7, font=FONTS['entry'],
                             bd=0, relief='flat', bg=bg,
                             highlightbackground=COLORS['border'], highlightthickness=1)
                e.grid(row=i+1, column=j+1, padx=1, pady=1)
                row_entries.append(e)
            self._entry_cells.append(row_entries)

            xbar_lbl = tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                                bg='#E8F5E9', fg=COLORS['text'], width=8)
            xbar_lbl.grid(row=i+1, column=n+1, padx=1, pady=1)
            self._xbar_labels.append(xbar_lbl)

            r_lbl = tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                             bg='#FFF8E1', fg=COLORS['text'], width=8)
            r_lbl.grid(row=i+1, column=n+2, padx=1, pady=1)
            self._range_labels.append(r_lbl)

    # ── Panel derecho ─────────────────────────────────────────────────────────
    def _build_right(self, parent):
        # Resultados numéricos (fijo en la parte superior)
        res = tk.Frame(parent, bg=COLORS['bg_card'],
                       highlightbackground=COLORS['border'], highlightthickness=1)
        res.pack(fill='x', padx=6, pady=(0, 4))
        self._build_results(res)

        # Área con scroll vertical para las tres cartas desplegables
        scroll_outer = tk.Frame(parent, bg=COLORS['bg'])
        scroll_outer.pack(fill='both', expand=True, padx=6, pady=4)

        cv = tk.Canvas(scroll_outer, bg=COLORS['bg'], highlightthickness=0)
        vsb = ttk.Scrollbar(scroll_outer, orient='vertical', command=cv.yview)
        cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        cv.pack(side='left', fill='both', expand=True)

        chart_f = tk.Frame(cv, bg=COLORS['bg'])
        _cw = cv.create_window((0, 0), window=chart_f, anchor='nw')

        # Actualizar scrollregion cuando cambien los widgets internos
        chart_f.bind('<Configure>',
                     lambda e: cv.configure(scrollregion=cv.bbox('all')))
        # Hacer que el frame interno ocupe todo el ancho del canvas
        cv.bind('<Configure>',
                lambda e: cv.itemconfig(_cw, width=e.width))
        # Scroll con la rueda del ratón sobre el canvas
        cv.bind('<MouseWheel>',
                lambda e: cv.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        self._build_charts(chart_f)

    def _build_results(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Límites de Control Calculados', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)

        self.result_labels = {}
        fields = [
            ('X̄̄', 'xbar_bar', '—'), ('R̄', 'r_bar', '—'), ('σ̂', 'sigma_est', '—'),
            ('LCS X̄', 'ucl_x', '—'), ('LC X̄', 'cl_x', '—'), ('LCI X̄', 'lcl_x', '—'),
            ('LCS R', 'ucl_r', '—'), ('LC R', 'cl_r', '—'), ('LCI R', 'lcl_r', '—'),
        ]
        for i, (label, key, default) in enumerate(fields):
            r, c = divmod(i, 3)
            f = tk.Frame(body, bg=COLORS['bg_card'])
            f.grid(row=r, column=c, padx=10, pady=4, sticky='w')
            tk.Label(f, text=label + ':', font=FONTS['label_b'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light'],
                     width=8, anchor='e').pack(side='left')
            lbl = tk.Label(f, text=default, font=FONTS['result'],
                           bg=COLORS['bg_card'], fg=COLORS['primary'], width=10, anchor='w')
            lbl.pack(side='left')
            self.result_labels[key] = lbl

        # Estado del proceso
        self.estado_lbl = tk.Label(body, text='', font=FONTS['subheader'],
                                   bg=COLORS['bg_card'], fg=COLORS['text'])
        self.estado_lbl.grid(row=3, column=0, columnspan=3, pady=(4, 0), sticky='w', padx=10)

    def _build_charts(self, parent):
        self._cc_x = CollapsibleChart(
            parent, 'Carta X̄ – Media del Proceso', figsize=(9, 2.8))
        self._cc_x.pack(fill='x', pady=(0, 3))
        self.ax_x = self._cc_x.ax

        self._cc_r = CollapsibleChart(
            parent, 'Carta R – Rango del Proceso', figsize=(9, 2.8))
        self._cc_r.pack(fill='x', pady=(0, 3))
        self.ax_r = self._cc_r.ax

        self._build_power_section(parent)
        self._draw_empty()

    def _draw_all(self):
        self._cc_x.fig.tight_layout(pad=1.5)
        self._cc_r.fig.tight_layout(pad=1.5)
        self._cc_x.draw()
        self._cc_r.draw()

    def _draw_empty(self):
        for ax, title in [(self.ax_x, 'Carta X̄ – Media del Proceso'),
                          (self.ax_r, 'Carta R – Rango del Proceso')]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
            ax.tick_params(labelsize=8)
        self._draw_all()

    # ── Lógica ───────────────────────────────────────────────────────────────
    def _on_fase_change(self, event=None):
        pass  # podría pre-llenar límites desde cache

    def _get_table_data(self):
        n = self.n_var.get()
        data = []
        for i, row_entries in enumerate(self._entry_cells):
            row = []
            for e in row_entries[:n]:
                v = parse_value(e.get())
                if v is not None:
                    row.append(v)
            if len(row) == n:
                data.append(row)
            elif len(row) > 0:
                break
        return data

    def _run(self):
        data = self._get_table_data()
        if len(data) < 2:
            messagebox.showwarning('Datos insuficientes',
                                   'Ingrese al menos 2 subgrupos completos.')
            return
        n = self.n_var.get()
        try:
            xbars, ranges = compute_xbar_r(data)
            # Actualizar columnas X̄ y R en la tabla
            for i, (xb, rg) in enumerate(zip(xbars, ranges)):
                self._xbar_labels[i].configure(text=f'{xb:.4f}')
                self._range_labels[i].configure(text=f'{rg:.4f}')

            # Límites manuales o calculados
            lim = self._read_manual_limits()
            if lim is None:
                lim = compute_control_limits_xr(xbars, ranges, n)
                self._fill_limit_entries(lim)
            self._limits_cache = lim

            # Especificaciones
            lie = parse_value(self.spec_entries['lie'].get())
            lse = parse_value(self.spec_entries['lse'].get())
            target = parse_value(self.spec_entries['target'].get())

            # Detección de fuera de control
            ooc_x = detect_out_of_control(xbars, lim['ucl_x'], lim['lcl_x'])
            ooc_r = detect_out_of_control(ranges, lim['ucl_r'], lim['lcl_r'])

            # Reglas de Western Electric (sobre carta X̄ y carta R)
            we_x = western_electric_rules(xbars, lim['ucl_x'], lim['cl_x'], lim['lcl_x'])
            we_r = western_electric_rules(ranges, lim['ucl_r'], lim['cl_r'], lim['lcl_r'])

            self._update_results(lim, ooc_x, ooc_r, we_x, we_r)
            self._draw_charts(xbars, ranges, lim, ooc_x, ooc_r, we_x, we_r, lie, lse, target)
        except Exception as e:
            messagebox.showerror('Error de cálculo', str(e))

    def _read_manual_limits(self):
        keys = ['lc_x', 'ucs_x', 'lci_x', 'lc_r', 'ucs_r']
        vals = {k: parse_value(self.lim_entries[k].get()) for k in keys}
        if all(v is not None for v in vals.values()):
            ucl_x, cl_x = vals['ucs_x'], vals['lc_x']
            n = self.n_var.get()
            # Derivar σ desde los límites de la carta X̄: σ = (UCL_X − CL_X)/3 × √n
            sigma_est = (ucl_x - cl_x) / 3 * np.sqrt(n) if ucl_x > cl_x and n > 0 else None
            return {
                'xbar_bar': vals['lc_x'], 'cl_x': vals['lc_x'],
                'ucl_x': vals['ucs_x'],  'lcl_x': vals['lci_x'],
                'cl_r':  vals['lc_r'],   'ucl_r': vals['ucs_r'],
                'lcl_r': 0.0,            'r_bar': vals['lc_r'],
                'sigma_est': sigma_est,
            }
        return None

    def _fill_limit_entries(self, lim):
        mapping = {
            'lc_x': lim['cl_x'],  'ucs_x': lim['ucl_x'],
            'lci_x': lim['lcl_x'], 'lc_r': lim['cl_r'],
            'ucs_r': lim['ucl_r'],
        }
        for key, val in mapping.items():
            e = self.lim_entries[key]
            e.delete(0, 'end')
            e.insert(0, f'{val:.5f}')

    def _update_results(self, lim, ooc_x, ooc_r, we_x=None, we_r=None):
        fmt = {
            'xbar_bar': f"{lim['xbar_bar']:.4f} lb",
            'r_bar':    f"{lim['r_bar']:.4f} lb",
            'sigma_est': f"{lim.get('sigma_est', 0):.5f} lb" if lim.get('sigma_est') else '—',
            'ucl_x': f"{lim['ucl_x']:.4f} lb",
            'cl_x':  f"{lim['cl_x']:.4f} lb",
            'lcl_x': f"{lim['lcl_x']:.4f} lb",
            'ucl_r': f"{lim['ucl_r']:.4f} lb",
            'cl_r':  f"{lim['cl_r']:.4f} lb",
            'lcl_r': f"{lim['lcl_r']:.4f} lb",
        }
        for key, lbl in self.result_labels.items():
            lbl.configure(text=fmt.get(key, '—'))

        total_ooc = len(ooc_x) + len(ooc_r)
        # Contar violaciones WE (reglas 2-6) excluyendo los ya marcados OOC
        we_count = 0
        if we_x:
            we_pts_x = set().union(*[set(we_x[k]) for k in range(2, 7) if we_x[k]])
            we_count += len(we_pts_x - set(ooc_x))
        if we_r:
            we_pts_r = set().union(*[set(we_r[k]) for k in range(2, 7) if we_r[k]])
            we_count += len(we_pts_r - set(ooc_r))

        if total_ooc == 0 and we_count == 0:
            msg   = '✔ Proceso bajo control estadístico'
            color = COLORS['success']
        else:
            parts = []
            if total_ooc:
                parts.append(f'{total_ooc} punto(s) fuera de límites')
            if we_count:
                parts.append(f'{we_count} violación(es) Reglas WE')
            msg   = '✘ ' + '  |  '.join(parts)
            color = COLORS['danger']
        self.estado_lbl.configure(text=msg, fg=color)

    def _draw_charts(self, xbars, ranges, lim, ooc_x, ooc_r,
                     we_x=None, we_r=None, lie=None, lse=None, target=None):
        sg = list(range(1, len(xbars)+1))

        # Puntos WE por carta (reglas 2-6, sin OOC)
        we_pts_x = set()
        we_pts_r = set()
        if we_x:
            we_pts_x = set().union(*[set(we_x[k]) for k in range(2, 7) if we_x[k]]) - set(ooc_x)
        if we_r:
            we_pts_r = set().union(*[set(we_r[k]) for k in range(2, 7) if we_r[k]]) - set(ooc_r)

        for ax, values, ucl, cl, lcl, ooc, we_pts, ylabel, title, spec_u, spec_l, tgt in [
            (self.ax_x, xbars, lim['ucl_x'], lim['cl_x'], lim['lcl_x'],
             ooc_x, we_pts_x, 'Media X̄ (lb)', 'Carta X̄ – Media del Proceso',
             lse, lie, target),
            (self.ax_r, ranges, lim['ucl_r'], lim['cl_r'], lim['lcl_r'],
             ooc_r, we_pts_r, 'Rango R (lb)', 'Carta R – Rango del Proceso',
             None, None, None),
        ]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')

            # Líneas de control
            ax.axhline(ucl, color=COLORS['chart_ucl'], linewidth=1.5, linestyle='--', label=f'LCS = {ucl:.4f}')
            ax.axhline(cl,  color=COLORS['chart_cl'],  linewidth=1.5, linestyle='-',  label=f'LC  = {cl:.4f}')
            ax.axhline(lcl, color=COLORS['chart_lcl'], linewidth=1.5, linestyle='--', label=f'LCI = {lcl:.4f}')

            # Líneas de especificación
            if spec_u is not None:
                ax.axhline(spec_u, color=COLORS['chart_spec_u'], linewidth=1.0,
                           linestyle=':', label=f'LSE = {spec_u:.3f}')
            if spec_l is not None:
                ax.axhline(spec_l, color=COLORS['chart_spec_l'], linewidth=1.0,
                           linestyle=':', label=f'LIE = {spec_l:.3f}')
            if tgt is not None:
                ax.axhline(tgt, color=COLORS['chart_target'], linewidth=1.0,
                           linestyle='-.', label=f'Objetivo = {tgt:.3f}', alpha=0.7)

            # Datos
            ax.plot(sg, values, color=COLORS['chart_data'], linewidth=1.2,
                    marker='o', markersize=4, zorder=3)

            # Puntos fuera de control en rojo
            for idx in ooc:
                ax.plot(sg[idx], values[idx], 'o', color=COLORS['chart_out'],
                        markersize=8, zorder=5, label='_nolegend_')
                ax.annotate(f'SG {sg[idx]}', (sg[idx], values[idx]),
                            textcoords='offset points', xytext=(4, 4),
                            fontsize=7, color=COLORS['chart_out'])

            # Marcadores WE (diamante naranja – reglas de patrón)
            _we_labeled = False
            for idx in sorted(we_pts):
                if idx < len(sg):
                    lbl = 'Regla WE' if not _we_labeled else '_nolegend_'
                    ax.plot(sg[idx], values[idx], 'D', color=COLORS['warning'],
                            markersize=7, zorder=4, label=lbl, markeredgecolor='#E65100',
                            markeredgewidth=0.8)
                    _we_labeled = True

            ax.set_xlabel('Número de Subgrupo', fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.set_xlim(0.5, len(sg)+0.5)
            ax.tick_params(labelsize=8)
            ax.legend(fontsize=7, loc='upper right', ncol=2)
            ax.grid(True, alpha=0.3, linestyle=':')

        self._draw_all()

    def _load_excel(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_read_subgroups
        fp = filedialog.askopenfilename(
            title='Seleccionar archivo Excel – Subgrupos',
            filetypes=[('Excel', '*.xlsx *.xls'), ('Todos', '*.*')])
        if not fp:
            return
        try:
            raw = excel_read_subgroups(fp)
            if not raw:
                messagebox.showwarning('Sin datos',
                    'No se encontraron subgrupos en la hoja.\n'
                    'Fila 1 = encabezados, filas 2+ = subgrupos.')
                return
            # Detectar si primera columna es índice (número entero del subgrupo)
            data = []
            for row in raw:
                if len(row) >= 2:
                    # Si el primer valor parece ser un número de subgrupo (entero pequeño)
                    if row[0] == int(row[0]) and 1 <= row[0] <= MAX_SUBGROUPS:
                        data.append(row[1:])
                    else:
                        data.append(row)
                elif len(row) == 1:
                    pass  # fila incompleta, ignorar
            if not data:
                messagebox.showwarning('Sin datos', 'No se pudieron leer subgrupos válidos.')
                return

            n_detected = len(data[0])
            if not (2 <= n_detected <= MAX_N):
                messagebox.showwarning('Tamaño no soportado',
                    f'Se detectó n={n_detected} observaciones por subgrupo.\n'
                    f'El software soporta n entre 2 y {MAX_N}.')
                return

            if self.n_var.get() != n_detected:
                self.n_var.set(n_detected)
                self._rebuild_table()

            self._clear_table(confirm=False)
            for i, row in enumerate(data):
                if i >= MAX_SUBGROUPS:
                    break
                for j, val in enumerate(row):
                    if j < len(self._entry_cells[i]):
                        self._entry_cells[i][j].delete(0, 'end')
                        self._entry_cells[i][j].insert(0, str(round(val, 5)))

            messagebox.showinfo('Excel cargado',
                f'{len(data)} subgrupos cargados (n={n_detected}).')
        except Exception as e:
            messagebox.showerror('Error al leer Excel', str(e))

    def _gen_template(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_create_template
        fp = filedialog.asksaveasfilename(
            title='Guardar plantilla Excel',
            defaultextension='.xlsx',
            initialfile='Plantilla_CartasXR.xlsx',
            filetypes=[('Excel', '*.xlsx')])
        if not fp:
            return
        try:
            excel_create_template(fp, 'subgroups')
            messagebox.showinfo('Plantilla creada',
                f'Plantilla guardada en:\n{fp}\n\n'
                'Formato: fila 1 = encabezados (Subgrupo, X1, X2...), '
                'filas 2+ = datos de subgrupos.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _load_fase1(self):
        self._load_data(FASE_I_DATA)

    def _load_fase2(self):
        self._load_data(FASE_II_DATA)
        # Si hay límites cacheados de Fase I, pre-llenarlos
        if self._limits_cache:
            self._fill_limit_entries(self._limits_cache)

    def _load_data(self, data):
        n_needed = len(data[0]) if data else 6
        if self.n_var.get() != n_needed:
            self.n_var.set(n_needed)
            self._rebuild_table()
        self._clear_table(confirm=False)
        for i, row in enumerate(data):
            if i >= MAX_SUBGROUPS:
                break
            for j, val in enumerate(row):
                if j < len(self._entry_cells[i]):
                    self._entry_cells[i][j].delete(0, 'end')
                    self._entry_cells[i][j].insert(0, str(val))

    def _clear_table(self, confirm=True):
        if confirm:
            if not messagebox.askyesno('Confirmar', '¿Limpiar todos los datos de la tabla?'):
                return
        for row in self._entry_cells:
            for e in row:
                e.delete(0, 'end')
        for lbl in self._xbar_labels + self._range_labels:
            lbl.configure(text='')
        for lbl in self.result_labels.values():
            lbl.configure(text='—')
        self.estado_lbl.configure(text='')
        for e in self.lim_entries.values():
            e.delete(0, 'end')
        self._draw_empty()

    # ── Potencia Fase II ──────────────────────────────────────────────────────

    def _build_power_section(self, parent):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill='x', pady=(4, 0))

        hdr = tk.Frame(outer, bg=COLORS['primary_light'], cursor='hand2')
        hdr.pack(fill='x')
        self._pw_arrow = tk.Label(hdr, text='▶', font=FONTS['label_b'],
                                   bg=COLORS['primary_light'], fg=COLORS['text_white'],
                                   cursor='hand2', padx=10, pady=5)
        self._pw_arrow.pack(side='right')
        title_lbl = tk.Label(hdr, text='Curva de Potencia – Corrimiento en la Media',
                              font=FONTS['label_b'], bg=COLORS['primary_light'],
                              fg=COLORS['text_white'], padx=10, pady=5, anchor='w')
        title_lbl.pack(side='left', fill='x', expand=True)
        for w in (hdr, self._pw_arrow, title_lbl):
            w.bind('<Button-1>', self._toggle_power)

        self._pw_body = tk.Frame(outer, bg=COLORS['bg_card'])
        self._pw_expanded = False

        # Controles de entrada
        ctrl = tk.Frame(self._pw_body, bg=COLORS['bg_card'])
        ctrl.pack(fill='x', padx=10, pady=(8, 4))
        fields = [('δ mín (σ):', 'dmin', '0.0'),
                  ('δ máx (σ):', 'dmax', '3.0'),
                  ('Paso (σ):', 'step', '0.25')]
        self._pw_entries = {}
        for col, (lbl_txt, key, default) in enumerate(fields):
            tk.Label(ctrl, text=lbl_txt, font=FONTS['label_b'],
                     bg=COLORS['bg_card'], fg=COLORS['text']).grid(
                         row=0, column=col * 2, sticky='e',
                         padx=(12 if col else 0, 3))
            e = tk.Entry(ctrl, width=6, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, default)
            e.grid(row=0, column=col * 2 + 1, padx=(0, 4))
            self._pw_entries[key] = e
        tk.Button(ctrl, text='Calcular Potencia', command=self._calc_power,
                  bg=COLORS['primary'], fg=COLORS['text_white'],
                  font=FONTS['label_b'], relief='flat', bd=0,
                  cursor='hand2', padx=8, pady=4).grid(row=0, column=6, padx=(10, 0))

        # Tira de resumen
        sum_f = tk.Frame(self._pw_body, bg=COLORS['bg_card'])
        sum_f.pack(fill='x', padx=10, pady=(2, 6))
        summary_defs = [
            ('1s', 'Potencia  δ=1σ'),
            ('2s', 'Potencia  δ=2σ'),
            ('3s', 'Potencia  δ=3σ'),
            ('d90', 'δ mín (90%)'),
            ('d50', 'δ mín (50%)'),
        ]
        self._pw_sum_lbls = {}
        for col, (key, header) in enumerate(summary_defs):
            f = tk.Frame(sum_f, bg=COLORS['bg_row_alt'],
                         highlightbackground=COLORS['border'], highlightthickness=1)
            f.grid(row=0, column=col, padx=3, pady=2, sticky='ew')
            tk.Label(f, text=header, font=FONTS['small'],
                     bg=COLORS['bg_row_alt'], fg=COLORS['text_light']).pack(
                         padx=4, pady=(3, 0))
            lbl = tk.Label(f, text='—', font=FONTS['result'],
                           bg=COLORS['bg_row_alt'], fg=COLORS['primary'])
            lbl.pack(padx=4, pady=(0, 3))
            self._pw_sum_lbls[key] = lbl
        for col in range(5):
            sum_f.grid_columnconfigure(col, weight=1)

        # Tabla desplazable
        tbl_wrap = tk.Frame(self._pw_body, bg=COLORS['border'], bd=1)
        tbl_wrap.pack(fill='x', padx=10, pady=(0, 4))
        tbl_cv = tk.Canvas(tbl_wrap, bg=COLORS['bg_card'],
                           height=130, highlightthickness=0)
        tbl_sb = ttk.Scrollbar(tbl_wrap, orient='vertical', command=tbl_cv.yview)
        tbl_cv.configure(yscrollcommand=tbl_sb.set)
        tbl_sb.pack(side='right', fill='y')
        tbl_cv.pack(side='left', fill='both', expand=True)
        tbl_f = tk.Frame(tbl_cv, bg=COLORS['bg_card'])
        tbl_cv.create_window((0, 0), window=tbl_f, anchor='nw')
        tbl_f.bind('<Configure>', lambda e: tbl_cv.configure(
            scrollregion=tbl_cv.bbox('all')))
        tbl_cv.bind('<MouseWheel>', lambda e: tbl_cv.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))

        for j, (h, w) in enumerate(zip(
                ['δ (σ)', 'δ (real)', 'Potencia', 'β', 'NRL'],
                [8, 10, 12, 10, 10])):
            tk.Label(tbl_f, text=h, font=FONTS['label_b'],
                     bg=COLORS['primary'], fg=COLORS['text_white'],
                     width=w, pady=3).grid(row=0, column=j, padx=1, pady=(0, 1))

        self._pw_tbl_rows = []
        for i in range(30):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            cells = []
            for j, w in enumerate([8, 10, 12, 10, 10]):
                lbl = tk.Label(tbl_f, text='', font=FONTS['small'],
                               bg=bg, fg=COLORS['text'], width=w, pady=2)
                lbl.grid(row=i + 1, column=j, padx=1, pady=1)
                cells.append(lbl)
            self._pw_tbl_rows.append(cells)

        # Gráfica de curva de potencia
        chart_f = tk.Frame(self._pw_body, bg=COLORS['bg'])
        chart_f.pack(fill='both', expand=True, padx=10, pady=(0, 8))
        self._pw_fig = Figure(figsize=(9, 2.5), facecolor=COLORS['bg'])
        self._pw_ax = self._pw_fig.add_subplot(1, 1, 1)
        self._pw_cv = FigureCanvasTkAgg(self._pw_fig, master=chart_f)
        self._pw_cv.get_tk_widget().pack(fill='both', expand=True)
        self._draw_power_empty()

    def _toggle_power(self, event=None):
        if self._pw_expanded:
            self._pw_body.pack_forget()
            self._pw_arrow.configure(text='▶')
        else:
            self._pw_body.pack(fill='x')
            self._pw_arrow.configure(text='▼')
        self._pw_expanded = not self._pw_expanded

    def _draw_power_empty(self):
        ax = self._pw_ax
        ax.clear()
        ax.set_facecolor('#FAFAFA')
        ax.set_title('Curva de Potencia – Carta X̄', fontsize=10,
                     fontweight='bold', color=COLORS['text'])
        ax.text(0.5, 0.5,
                'Calcule las cartas de control primero,\n'
                'luego expanda esta sección y presione "Calcular Potencia"',
                ha='center', va='center', transform=ax.transAxes,
                color=COLORS['text_light'], fontsize=9, style='italic',
                multialignment='center')
        ax.tick_params(labelsize=8)
        self._pw_cv.draw()

    def _calc_power(self):
        lim = self._limits_cache
        if lim is None:
            lim = self._read_manual_limits()
        if lim is None:
            messagebox.showwarning('Sin límites',
                'Presione "Calcular cartas" primero para obtener los límites.')
            return
        sigma = lim.get('sigma_est')
        if not sigma or sigma <= 0:
            messagebox.showwarning('σ no disponible',
                'No se pudo estimar σ.\n'
                'Ingrese los límites de la carta X̄ y presione "Calcular cartas".')
            return

        try:
            d_min = float(self._pw_entries['dmin'].get().replace(',', '.'))
            d_max = float(self._pw_entries['dmax'].get().replace(',', '.'))
            step  = float(self._pw_entries['step'].get().replace(',', '.'))
            assert step > 0 and d_max > d_min and d_min >= 0
        except Exception:
            messagebox.showwarning('Parámetros inválidos',
                'Verifique: δ mín ≥ 0, δ máx > δ mín, Paso > 0.')
            return

        n = self.n_var.get()
        delta_range = np.arange(d_min, d_max + step * 0.001, step)
        delta_range = delta_range[delta_range <= d_max + 1e-9]
        if len(delta_range) > 50:
            delta_range = delta_range[:50]
            messagebox.showinfo('Puntos limitados',
                'Se calcularon los primeros 50 puntos.\nReduzca el rango o aumente el paso.')

        try:
            results = compute_power_curve(
                lim['ucl_x'], lim['lcl_x'], lim['cl_x'], sigma, n, delta_range)
        except Exception as ex:
            messagebox.showerror('Error de cálculo', str(ex))
            return

        # Limpiar tabla
        for cells in self._pw_tbl_rows:
            for c in cells:
                c.configure(text='', fg=COLORS['text'], font=FONTS['small'])

        # Llenar tabla
        for i, r in enumerate(results):
            if i >= len(self._pw_tbl_rows):
                break
            p = r['poder']
            p_col = (COLORS['success'] if p >= 0.90
                     else (COLORS['warning'] if p >= 0.50 else COLORS['danger']))
            arl_txt = f"{r['arl']:.1f}" if r['arl'] < 99999 else '∞'
            row_vals = [f"{r['delta_sigma']:.2f}", f"{r['delta_real']:.5f}",
                        f"{p * 100:.1f}%", f"{r['beta'] * 100:.1f}%", arl_txt]
            for j, (cell, val) in enumerate(zip(self._pw_tbl_rows[i], row_vals)):
                if j == 2:
                    cell.configure(text=val, fg=p_col, font=FONTS['label_b'])
                else:
                    cell.configure(text=val)

        # Tira de resumen
        for key, d_sigma in [('1s', 1.0), ('2s', 2.0), ('3s', 3.0)]:
            r = compute_arl(lim['ucl_x'], lim['lcl_x'], lim['cl_x'],
                            sigma, n, delta=d_sigma * sigma)
            p = r['poder']
            self._pw_sum_lbls[key].configure(
                text=f'{p * 100:.1f}%',
                fg=(COLORS['success'] if p >= 0.90
                    else (COLORS['warning'] if p >= 0.50 else COLORS['danger'])))

        def first_above(threshold):
            for r in results:
                if r['poder'] >= threshold:
                    return r['delta_sigma']
            return None

        for key, thr in [('d90', 0.90), ('d50', 0.50)]:
            d = first_above(thr)
            self._pw_sum_lbls[key].configure(
                text=f'{d:.2f}σ' if d is not None else '>δ máx',
                fg=COLORS['text'])

        # Curva suavizada (300 puntos)
        deltas_smooth = np.linspace(d_min, d_max, 300)
        powers_smooth = [
            compute_arl(lim['ucl_x'], lim['lcl_x'], lim['cl_x'],
                        sigma, n, delta=float(d) * sigma)['poder'] * 100
            for d in deltas_smooth
        ]

        ax = self._pw_ax
        ax.clear()
        ax.set_facecolor('#FAFAFA')
        ax.plot(deltas_smooth, powers_smooth, color=COLORS['primary'],
                linewidth=2, zorder=3, label='Potencia')
        ax.fill_between(deltas_smooth, powers_smooth,
                        alpha=0.12, color=COLORS['primary'])
        ax.scatter([r['delta_sigma'] for r in results],
                   [r['poder'] * 100 for r in results],
                   color=COLORS['primary'], s=28, zorder=4)
        ax.axhline(90, color=COLORS['chart_ucl'], linewidth=1.2,
                   linestyle='--', label='90%', alpha=0.9)
        ax.axhline(50, color=COLORS['warning'], linewidth=1.0,
                   linestyle=':', label='50%', alpha=0.8)
        ax.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
        ax.set_ylabel('Potencia (%)', fontsize=8)
        ax.set_title('Curva de Potencia – Carta X̄', fontsize=10,
                     fontweight='bold', color=COLORS['text'])
        ax.set_ylim(-2, 107)
        span = d_max - d_min
        ax.set_xlim(d_min - 0.03 * span, d_max + 0.03 * span)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=7, loc='lower right')
        ax.grid(True, alpha=0.3, linestyle=':')
        self._pw_fig.tight_layout(pad=1.2)
        self._pw_cv.draw()
