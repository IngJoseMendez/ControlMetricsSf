# -*- coding: utf-8 -*-
"""
Módulo: Cartas de Control I – MR  (Valores Individuales y Rango Móvil)
ControlMetrics
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS
from utils.spc_utils import (compute_imr, compute_control_limits_imr,
                              detect_out_of_control, parse_value,
                              western_electric_rules)
from utils.widgets import CollapsibleChart

MAX_OBS = 120


class CartasIMRModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._limits_cache = None
        self._build_ui()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self, text=(
            "Ingrese observaciones individuales (una por fila). "
            "Indicado cuando n=1 por subgrupo o no es posible agrupar mediciones."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=900, justify='left').pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=6, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=320, width=360)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=480)
        self._build_right(right)

    # ── Panel izquierdo ───────────────────────────────────────────────────────
    def _build_left(self, parent):
        sc = tk.Canvas(parent, bg=COLORS['bg_card'], highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient='vertical', command=sc.yview)
        sc.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        sc.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(sc, bg=COLORS['bg_card'])
        sc.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e: sc.configure(scrollregion=sc.bbox('all')))
        sc.bind('<MouseWheel>', lambda e: sc.yview_scroll(int(-1*(e.delta/120)), 'units'))
        parent = inner

        tk.Frame(parent, bg=COLORS['primary_light'], pady=6).pack(fill='x')
        tk.Label(parent.winfo_children()[-1], text='Observaciones Individuales',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, side='left')

        # Fase
        ctrl = tk.Frame(parent, bg=COLORS['bg_card'], pady=6)
        ctrl.pack(fill='x', padx=10)
        tk.Label(ctrl, text='Fase:', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).grid(row=0, column=0, sticky='e', padx=(0, 4))
        self.fase_var = tk.StringVar(value='I')
        ttk.Combobox(ctrl, textvariable=self.fase_var, width=20, state='readonly',
                     values=['I – Estabilización', 'II – Monitoreo']).grid(row=0, column=1, sticky='w')

        # Límites Fase II
        lf = tk.LabelFrame(parent, text='Límites de Control (opcional – Fase II)',
                           bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        lf.pack(fill='x', padx=10, pady=(4, 2))
        li = tk.Frame(lf, bg=COLORS['bg_card'])
        li.pack(fill='x', padx=6, pady=4)
        self.lim_entries = {}
        for idx, (lbl, key) in enumerate([('LC-I:', 'lc_i'), ('LCS-I:', 'ucs_i'),
                                           ('LCI-I:', 'lci_i'), ('LCS-MR:', 'ucs_mr')]):
            r, c = divmod(idx, 2)
            tk.Label(li, text=lbl, font=FONTS['small'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light']).grid(row=r, column=c*2, sticky='e', padx=(6, 2), pady=2)
            e = tk.Entry(li, width=9, font=FONTS['entry'], bd=1, relief='solid')
            e.grid(row=r, column=c*2+1, sticky='w', padx=(0, 8), pady=2)
            self.lim_entries[key] = e

        # Especificaciones
        sf = tk.LabelFrame(parent, text='Especificaciones del Cliente',
                           bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        sf.pack(fill='x', padx=10, pady=(2, 4))
        si = tk.Frame(sf, bg=COLORS['bg_card'])
        si.pack(fill='x', padx=6, pady=4)
        self.spec_entries = {}
        for idx, (lbl, key, val) in enumerate([
                ('LIE:', 'lie', DEFAULTS['lie_cliente']),
                ('LSE:', 'lse', DEFAULTS['lse_cliente']),
                ('Obj:', 'target', DEFAULTS['target'])]):
            tk.Label(si, text=lbl, font=FONTS['small'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light']).grid(row=0, column=idx*2, sticky='e', padx=(4, 2))
            e = tk.Entry(si, width=7, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, str(val))
            e.grid(row=0, column=idx*2+1, sticky='w', padx=(0, 6))
            self.spec_entries[key] = e

        # Tabla
        tbl_hdr = tk.Frame(parent, bg=COLORS['primary'], pady=3)
        tbl_hdr.pack(fill='x', padx=10, pady=(4, 0))
        self._tbl_hdr_frame = tbl_hdr
        tk.Button(tbl_hdr, text='✕ Limpiar', command=self._clear_table,
                  bg=COLORS['primary'], fg='#FFCDD2', font=FONTS['small'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=2).pack(side='right', padx=6)
        self._tbl_collapsed = False
        self._tbl_toggle_btn = tk.Button(tbl_hdr, text='▲', command=self._toggle_table,
                  bg=COLORS['primary'], fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=6, pady=0)
        self._tbl_toggle_btn.pack(side='left', padx=(6, 2))
        tk.Label(tbl_hdr, text='Tabla de Datos Individuales', font=FONTS['label_b'],
                 bg=COLORS['primary'], fg=COLORS['text_white']).pack(side='left', padx=(0, 6))

        outer = tk.Frame(parent, bg=COLORS['border'], bd=1)
        outer.pack(fill='x', padx=10, pady=(0, 4))
        self.tbl_outer = outer

        self.canvas_tbl = tk.Canvas(outer, bg=COLORS['bg_card'], height=200, highlightthickness=0)
        vsb2 = ttk.Scrollbar(outer, orient='vertical', command=self.canvas_tbl.yview)
        self.canvas_tbl.configure(yscrollcommand=vsb2.set)
        vsb2.pack(side='right', fill='y')
        self.canvas_tbl.pack(side='left', fill='both', expand=True)
        self.tbl_inner = tk.Frame(self.canvas_tbl, bg=COLORS['bg_card'])
        self.canvas_tbl.create_window((0, 0), window=self.tbl_inner, anchor='nw')
        self.tbl_inner.bind('<Configure>', lambda e: self.canvas_tbl.configure(
            scrollregion=self.canvas_tbl.bbox('all')))
        self._build_data_table()

        # Botones
        bf = tk.Frame(parent, bg=COLORS['bg_card'])
        bf.pack(fill='x', padx=10, pady=(4, 0))
        for txt, cmd, bg, fg in [
                ('Calcular cartas', self._run, COLORS['primary'], COLORS['text_white']),
                ('Limpiar tabla',   self._clear_table, '#CFD8DC', COLORS['text'])]:
            tk.Button(bf, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Excel
        ef = tk.Frame(parent, bg=COLORS['bg_card'])
        ef.pack(fill='x', padx=10, pady=(6, 8))
        tk.Frame(ef, bg=COLORS['border'], height=1).pack(fill='x', pady=(0, 3))
        tk.Label(ef, text='📋 Excel: columna A = valores individuales (fila 1 = encabezado)',
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['text_light'], wraplength=340).pack(anchor='w')
        tk.Button(ef, text='📂 Cargar desde Excel', command=self._load_excel,
                  bg='#0277BD', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(
                      side='left', pady=4, padx=3)

    def _build_data_table(self):
        for w in self.tbl_inner.winfo_children():
            w.destroy()
        self._entry_cells = []
        self._mr_labels   = []
        for j, (h, w, bg) in enumerate(zip(
                ['Obs.', 'Valor (lb)', 'MR'],
                [5, 10, 8],
                [COLORS['primary'], COLORS['primary_light'], COLORS['bg_subheader']])):
            tk.Label(self.tbl_inner, text=h, font=FONTS['label_b'], bg=bg,
                     fg=COLORS['text_white'], width=w, pady=4).grid(
                         row=0, column=j, padx=1, pady=1, sticky='ew')
        for i in range(MAX_OBS):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            tk.Label(self.tbl_inner, text=str(i+1), font=FONTS['small'],
                     bg=COLORS['primary_lighter'], fg=COLORS['text_white'],
                     width=5).grid(row=i+1, column=0, padx=1, pady=1)
            e = tk.Entry(self.tbl_inner, width=10, font=FONTS['entry'],
                         bd=0, relief='flat', bg=bg,
                         highlightbackground=COLORS['border'], highlightthickness=1)
            e.grid(row=i+1, column=1, padx=1, pady=1)
            self._entry_cells.append(e)
            mr = tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                          bg='#FFF8E1', fg=COLORS['text'], width=8)
            mr.grid(row=i+1, column=2, padx=1, pady=1)
            self._mr_labels.append(mr)

    def _toggle_table(self):
        if self._tbl_collapsed:
            self.tbl_outer.pack(after=self._tbl_hdr_frame, fill='x', padx=10, pady=(0, 4))
            self._tbl_toggle_btn.configure(text='▲')
            self._tbl_collapsed = False
        else:
            self.tbl_outer.pack_forget()
            self._tbl_toggle_btn.configure(text='▼')
            self._tbl_collapsed = True

    # ── Panel derecho ─────────────────────────────────────────────────────────
    def _build_right(self, parent):
        res = tk.Frame(parent, bg=COLORS['bg_card'],
                       highlightbackground=COLORS['border'], highlightthickness=1)
        res.pack(fill='x', padx=6, pady=(0, 4))
        self._build_results(res)

        cf = tk.Frame(parent, bg=COLORS['bg'])
        cf.pack(fill='both', expand=True, padx=6, pady=4)
        self._cc_i  = CollapsibleChart(cf, 'Carta I – Valores Individuales', figsize=(9, 2.8))
        self._cc_i.pack(fill='both', expand=True, pady=(0, 2))
        self.ax_i = self._cc_i.ax
        self._cc_mr = CollapsibleChart(cf, 'Carta MR – Rango Móvil', figsize=(9, 2.8))
        self._cc_mr.pack(fill='both', expand=True, pady=(2, 0))
        self.ax_mr = self._cc_mr.ax
        self._draw_empty()

    def _build_results(self, parent):
        tk.Frame(parent, bg=COLORS['primary_light'], pady=5).pack(fill='x')
        tk.Label(parent.winfo_children()[-1], text='Límites de Control Calculados',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, anchor='w')
        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)
        self.result_labels = {}
        fields = [('X̄', 'x_bar'), ('MR̄', 'mr_bar'), ('σ̂', 'sigma_est'),
                  ('LCS I', 'ucl_i'), ('LC I', 'cl_i'), ('LCI I', 'lcl_i'),
                  ('LCS MR', 'ucl_mr'), ('LC MR', 'cl_mr')]
        for i, (lbl, key) in enumerate(fields):
            r, c = divmod(i, 4)
            f = tk.Frame(body, bg=COLORS['bg_card'])
            f.grid(row=r, column=c, padx=8, pady=3, sticky='w')
            tk.Label(f, text=lbl+':', font=FONTS['label_b'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light'], width=7, anchor='e').pack(side='left')
            lb = tk.Label(f, text='—', font=FONTS['result'], bg=COLORS['bg_card'],
                          fg=COLORS['primary'], width=10, anchor='w')
            lb.pack(side='left')
            self.result_labels[key] = lb
        self.estado_lbl = tk.Label(body, text='', font=FONTS['subheader'],
                                   bg=COLORS['bg_card'], fg=COLORS['text'])
        self.estado_lbl.grid(row=2, column=0, columnspan=4, pady=(2, 0), sticky='w', padx=8)

    def _draw_empty(self):
        for ax, title in [(self.ax_i,  'Carta I – Valores Individuales'),
                          (self.ax_mr, 'Carta MR – Rango Móvil')]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
            ax.tick_params(labelsize=8)
        self._cc_i.fig.tight_layout(pad=1.5);  self._cc_i.draw()
        self._cc_mr.fig.tight_layout(pad=1.5); self._cc_mr.draw()

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _get_data(self):
        data = []
        for e in self._entry_cells:
            v = parse_value(e.get())
            if v is not None:
                data.append(v)
            else:
                break
        return data

    def _run(self):
        data = self._get_data()
        if len(data) < 3:
            messagebox.showwarning('Datos insuficientes', 'Ingrese al menos 3 observaciones.')
            return
        try:
            ind, mr = compute_imr(data)
            for i, v in enumerate(mr):
                self._mr_labels[i+1].configure(text=f'{v:.4f}')

            lim = self._read_manual_limits()
            if lim is None:
                lim = compute_control_limits_imr(ind, mr)
                self._fill_limits(lim)
                self._limits_cache = lim

            ooc_i  = detect_out_of_control(ind, lim['ucl_i'],  lim['lcl_i'])
            ooc_mr = detect_out_of_control(mr,  lim['ucl_mr'], lim['lcl_mr'])

            lie    = parse_value(self.spec_entries['lie'].get())
            lse    = parse_value(self.spec_entries['lse'].get())
            target = parse_value(self.spec_entries['target'].get())

            # Reglas Western Electric
            we = western_electric_rules(ind, lim['ucl_i'], lim['cl_i'], lim['lcl_i'])

            self._update_results(lim, ooc_i, ooc_mr, we)
            self._draw_charts(ind, mr, lim, ooc_i, ooc_mr, we, lie, lse, target)
        except Exception as ex:
            messagebox.showerror('Error de cálculo', str(ex))

    def _read_manual_limits(self):
        vals = {k: parse_value(self.lim_entries[k].get())
                for k in ['lc_i', 'ucs_i', 'lci_i', 'ucs_mr']}
        if all(v is not None for v in vals.values()):
            mr_bar = vals['ucs_mr'] / 3.267
            return {'x_bar': vals['lc_i'], 'mr_bar': mr_bar,
                    'sigma_est': mr_bar/1.128,
                    'ucl_i': vals['ucs_i'], 'cl_i': vals['lc_i'], 'lcl_i': vals['lci_i'],
                    'ucl_mr': vals['ucs_mr'], 'cl_mr': mr_bar, 'lcl_mr': 0.0}
        return None

    def _fill_limits(self, lim):
        for key, val in [('lc_i', lim['cl_i']), ('ucs_i', lim['ucl_i']),
                          ('lci_i', lim['lcl_i']), ('ucs_mr', lim['ucl_mr'])]:
            e = self.lim_entries[key]; e.delete(0, 'end'); e.insert(0, f'{val:.5f}')

    def _update_results(self, lim, ooc_i, ooc_mr, we):
        for key, val in [('x_bar', lim['x_bar']), ('mr_bar', lim['mr_bar']),
                          ('sigma_est', lim['sigma_est']),
                          ('ucl_i', lim['ucl_i']), ('cl_i', lim['cl_i']),
                          ('lcl_i', lim['lcl_i']), ('ucl_mr', lim['ucl_mr']),
                          ('cl_mr', lim['cl_mr'])]:
            self.result_labels[key].configure(text=f'{val:.4f} lb')
        # Patrones
        viol_sets = [set(we[k]) for k in range(2, 7) if we[k]]
        all_we = set().union(*viol_sets) if viol_sets else set()
        total = len(set(ooc_i) | set(ooc_mr) | all_we)
        if total == 0:
            self.estado_lbl.configure(text='✔ Proceso bajo control estadístico',
                                      fg=COLORS['success'])
        else:
            we_count = len(all_we)
            msg = f'✘ {len(set(ooc_i)|set(ooc_mr))} fuera de límites'
            if we_count:
                msg += f'  |  {we_count} violación(es) WE'
            self.estado_lbl.configure(text=msg, fg=COLORS['danger'])

    def _draw_charts(self, ind, mr, lim, ooc_i, ooc_mr, we, lie, lse, target):
        configs = [
            (self.ax_i,  self._cc_i,  ind, lim['ucl_i'],  lim['cl_i'],  lim['lcl_i'],
             ooc_i, 'Valor (lb)', 'Carta I – Valores Individuales', lse, lie, target),
            (self.ax_mr, self._cc_mr, mr,  lim['ucl_mr'], lim['cl_mr'], lim['lcl_mr'],
             ooc_mr, 'Rango Móvil (lb)', 'Carta MR – Rango Móvil', None, None, None),
        ]
        # WE violations only on I chart
        we_pts = set().union(*[set(we[k]) for k in range(2, 7) if we[k]])

        for ax, cc, values, ucl, cl, lcl, ooc, ylabel, title, su, sl, tgt in configs:
            ax.clear(); ax.set_facecolor('#FAFAFA')
            sg = list(range(1, len(values)+1))
            ax.axhline(ucl, color=COLORS['chart_ucl'], lw=1.5, ls='--', label=f'LCS={ucl:.4f}')
            ax.axhline(cl,  color=COLORS['chart_cl'],  lw=1.5, ls='-',  label=f'LC={cl:.4f}')
            ax.axhline(lcl, color=COLORS['chart_lcl'], lw=1.5, ls='--', label=f'LCI={lcl:.4f}')
            if su is not None:
                ax.axhline(su, color=COLORS['chart_spec_u'], lw=1.0, ls=':', label=f'LSE={su:.3f}')
            if sl is not None:
                ax.axhline(sl, color=COLORS['chart_spec_l'], lw=1.0, ls=':', label=f'LIE={sl:.3f}')
            if tgt is not None:
                ax.axhline(tgt, color=COLORS['chart_target'], lw=1.0, ls='-.', label=f'Obj={tgt:.3f}', alpha=0.7)
            ax.plot(sg, values, color=COLORS['chart_data'], lw=1.2, marker='o', ms=4, zorder=3)
            for idx in ooc:
                ax.plot(sg[idx], values[idx], 'o', color=COLORS['chart_out'], ms=8, zorder=5)
                ax.annotate(str(sg[idx]), (sg[idx], values[idx]),
                            textcoords='offset points', xytext=(4, 4),
                            fontsize=7, color=COLORS['chart_out'])
            # WE markers (orange diamond) only on I chart
            if ax is self.ax_i:
                for idx in we_pts:
                    if idx not in ooc and idx < len(sg):
                        ax.plot(sg[idx], values[idx], 'D', color=COLORS['warning'],
                                ms=7, zorder=4, label='_nolegend_')
            ax.set_xlabel('Observación', fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.set_xlim(0.5, len(sg)+0.5)
            ax.tick_params(labelsize=8)
            ax.legend(fontsize=7, loc='upper right', ncol=2)
            ax.grid(True, alpha=0.3, ls=':')
            cc.fig.tight_layout(pad=1.5); cc.draw()

    def _load_excel(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_read_single_col
        fp = filedialog.askopenfilename(title='Seleccionar Excel',
            filetypes=[('Excel', '*.xlsx *.xls'), ('Todos', '*.*')])
        if not fp:
            return
        try:
            data = excel_read_single_col(fp)
            if not data:
                messagebox.showwarning('Sin datos', 'No se encontraron valores numéricos.'); return
            self._clear_table(confirm=False)
            for i, v in enumerate(data[:MAX_OBS]):
                self._entry_cells[i].delete(0, 'end')
                self._entry_cells[i].insert(0, str(round(v, 5)))
            messagebox.showinfo('Excel cargado', f'{min(len(data), MAX_OBS)} observaciones cargadas.')
        except Exception as ex:
            messagebox.showerror('Error', str(ex))

    def _clear_table(self, confirm=True):
        if confirm and not messagebox.askyesno('Confirmar', '¿Limpiar todos los datos?'):
            return
        for e in self._entry_cells:
            e.delete(0, 'end')
        for lb in self._mr_labels:
            lb.configure(text='')
        for lb in self.result_labels.values():
            lb.configure(text='—')
        self.estado_lbl.configure(text='')
        for e in self.lim_entries.values():
            e.delete(0, 'end')
        self._draw_empty()
