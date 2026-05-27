# -*- coding: utf-8 -*-
"""
Módulo: Cartas de Control X̄ – S  (Variables, desviación estándar muestral)
ControlMetrics
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS, SPC_CONSTANTS, FASE_I_DATA, FASE_II_DATA
from utils.spc_utils import (compute_xbar_s, compute_control_limits_xs,
                              detect_out_of_control, parse_value,
                              western_electric_rules)
from utils.widgets import CollapsibleChart

MAX_SUBGROUPS = 50
MAX_N         = 10


class CartasXSModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._limits_cache = None
        self._build_ui()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self, text=(
            "Ingrese los datos de cada subgrupo. La carta X̄-S usa la desviación estándar "
            "muestral S en lugar del rango R; recomendada para n ≥ 10."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=900, justify='left').pack(fill='x', padx=16, pady=(10, 4))

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
        sc = tk.Canvas(parent, bg=COLORS['bg_card'], highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient='vertical', command=sc.yview)
        sc.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y'); sc.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(sc, bg=COLORS['bg_card'])
        sc.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e: sc.configure(scrollregion=sc.bbox('all')))
        sc.bind('<MouseWheel>', lambda e: sc.yview_scroll(int(-1*(e.delta/120)), 'units'))
        parent = inner

        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Datos de Subgrupos (X̄-S)', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, side='left')

        # Controles fase / n
        ctrl = tk.Frame(parent, bg=COLORS['bg_card'], pady=6)
        ctrl.pack(fill='x', padx=10)
        tk.Label(ctrl, text='Fase:', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).grid(row=0, column=0, sticky='e', padx=(0, 4))
        self.fase_var = tk.StringVar(value='I')
        ttk.Combobox(ctrl, textvariable=self.fase_var, width=20, state='readonly',
                     values=['I – Estabilización', 'II – Monitoreo']).grid(row=0, column=1, sticky='w', pady=3)
        tk.Label(ctrl, text='Tamaño (n):', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).grid(row=0, column=2, sticky='e', padx=(12, 4))
        self.n_var = tk.IntVar(value=DEFAULTS['subgroup_size'])
        n_spin = ttk.Spinbox(ctrl, from_=2, to=MAX_N, textvariable=self.n_var,
                             width=5, command=self._safe_rebuild)
        n_spin.bind('<Return>', lambda e: self._safe_rebuild())
        n_spin.bind('<FocusOut>', lambda e: self._safe_rebuild())
        n_spin.grid(row=0, column=3, sticky='w', pady=3)

        # Límites opcionales
        lf = tk.LabelFrame(parent, text='Límites de Control (opcional – Fase II)',
                           bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        lf.pack(fill='x', padx=10, pady=(4, 2))
        li = tk.Frame(lf, bg=COLORS['bg_card']); li.pack(fill='x', padx=6, pady=4)
        lim_fields = [('X̄̄ (LC):', 'lc_x'), ('LCS-X:', 'ucs_x'), ('LCI-X:', 'lci_x'),
                      ('S̄ (LC):', 'lc_s'), ('LCS-S:', 'ucs_s')]
        self.lim_entries = {}
        for i, (lbl, key) in enumerate(lim_fields):
            r, c = divmod(i, 3)
            tk.Label(li, text=lbl, font=FONTS['small'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light']).grid(row=r, column=c*2, sticky='e', padx=(6, 2), pady=2)
            e = tk.Entry(li, width=8, font=FONTS['entry'], bd=1, relief='solid')
            e.grid(row=r, column=c*2+1, sticky='w', padx=(0, 8), pady=2)
            self.lim_entries[key] = e

        # Especificaciones
        sf = tk.LabelFrame(parent, text='Especificaciones del Cliente',
                           bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        sf.pack(fill='x', padx=10, pady=(2, 4))
        si = tk.Frame(sf, bg=COLORS['bg_card']); si.pack(fill='x', padx=6, pady=4)
        self.spec_entries = {}
        for i, (lbl, key, val) in enumerate([('LIE (lb):', 'lie', DEFAULTS['lie_cliente']),
                                              ('LSE (lb):', 'lse', DEFAULTS['lse_cliente']),
                                              ('Objetivo:', 'target', DEFAULTS['target'])]):
            tk.Label(si, text=lbl, font=FONTS['small'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light']).grid(row=0, column=i*2, sticky='e', padx=(6, 2))
            e = tk.Entry(si, width=8, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, str(val))
            e.grid(row=0, column=i*2+1, sticky='w', padx=(0, 8))
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
        self.tbl_title = tk.Label(tbl_hdr, text='Tabla de Subgrupos (n = 6)',
                 font=FONTS['label_b'], bg=COLORS['primary'],
                 fg=COLORS['text_white'])
        self.tbl_title.pack(side='left', padx=(0, 6))

        outer = tk.Frame(parent, bg=COLORS['border'], bd=1)
        outer.pack(fill='x', padx=10, pady=(0, 4))
        self.tbl_outer = outer

        self.canvas_tbl = tk.Canvas(outer, bg=COLORS['bg_card'], height=180, highlightthickness=0)
        vsb2 = ttk.Scrollbar(outer, orient='vertical',   command=self.canvas_tbl.yview)
        hsb  = ttk.Scrollbar(outer, orient='horizontal', command=self.canvas_tbl.xview)
        self.canvas_tbl.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb.set)
        vsb2.pack(side='right', fill='y'); hsb.pack(side='bottom', fill='x')
        self.canvas_tbl.pack(side='left', fill='both', expand=True)
        self.tbl_inner = tk.Frame(self.canvas_tbl, bg=COLORS['bg_card'])
        self.canvas_tbl.create_window((0, 0), window=self.tbl_inner, anchor='nw')
        self.tbl_inner.bind('<Configure>', lambda e: self.canvas_tbl.configure(
            scrollregion=self.canvas_tbl.bbox('all')))

        self._entry_cells = []
        self._xbar_labels = []
        self._s_labels    = []
        self._rebuild_table()

        # Botones – fila 1
        bf1 = tk.Frame(parent, bg=COLORS['bg_card'])
        bf1.pack(fill='x', padx=10, pady=(4, 0))
        for txt, cmd, bg, fg in [
                ('Calcular cartas', self._run, COLORS['primary'], COLORS['text_white']),
                ('Limpiar tabla',   self._clear_table, '#CFD8DC', COLORS['text'])]:
            tk.Button(bf1, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Botones – fila 2
        bf2 = tk.Frame(parent, bg=COLORS['bg_card'])
        bf2.pack(fill='x', padx=10, pady=(3, 4))
        for txt, cmd, bg, fg in [
                ('Cargar Fase I (estudio)',  self._load_fase1, COLORS['secondary'], COLORS['text']),
                ('Cargar Fase II (estudio)', self._load_fase2, '#F57F17', COLORS['text_white'])]:
            tk.Button(bf2, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

    def _safe_rebuild(self):
        try:
            n = max(2, min(MAX_N, self.n_var.get()))
            self.n_var.set(n)
        except Exception:
            self.n_var.set(DEFAULTS['subgroup_size'])
        self._rebuild_table()

    def _rebuild_table(self):
        n = self.n_var.get()
        self.tbl_title.configure(text=f'Tabla de Subgrupos (n = {n})')
        for w in self.tbl_inner.winfo_children():
            w.destroy()
        self._entry_cells.clear(); self._xbar_labels.clear(); self._s_labels.clear()

        headers   = ['SG'] + [f'X{i+1}' for i in range(n)] + ['X̄', 'S']
        col_widths = [4] + [7]*n + [8, 8]
        for j, (h, w) in enumerate(zip(headers, col_widths)):
            bg = (COLORS['primary'] if j == 0
                  else COLORS['primary_light'] if j <= n
                  else COLORS['bg_subheader'])
            tk.Label(self.tbl_inner, text=h, font=FONTS['label_b'], bg=bg,
                     fg=COLORS['text_white'], width=w, pady=4).grid(
                         row=0, column=j, padx=1, pady=1, sticky='ew')

        for i in range(MAX_SUBGROUPS):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            tk.Label(self.tbl_inner, text=str(i+1), font=FONTS['small'],
                     bg=COLORS['primary_lighter'], fg=COLORS['text_white'], width=4).grid(
                         row=i+1, column=0, padx=1, pady=1)
            row_ent = []
            for j in range(n):
                e = tk.Entry(self.tbl_inner, width=7, font=FONTS['entry'],
                             bd=0, relief='flat', bg=bg,
                             highlightbackground=COLORS['border'], highlightthickness=1)
                e.grid(row=i+1, column=j+1, padx=1, pady=1)
                row_ent.append(e)
            self._entry_cells.append(row_ent)
            xl = tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                          bg='#E8F5E9', fg=COLORS['text'], width=8)
            xl.grid(row=i+1, column=n+1, padx=1, pady=1)
            self._xbar_labels.append(xl)
            sl = tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                          bg='#FFF8E1', fg=COLORS['text'], width=8)
            sl.grid(row=i+1, column=n+2, padx=1, pady=1)
            self._s_labels.append(sl)

    def _toggle_table(self):
        if self._tbl_collapsed:
            self.tbl_outer.pack(after=self._tbl_hdr_frame, fill='x', padx=10, pady=(0, 4))
            self._tbl_toggle_btn.configure(text='▲'); self._tbl_collapsed = False
        else:
            self.tbl_outer.pack_forget()
            self._tbl_toggle_btn.configure(text='▼'); self._tbl_collapsed = True

    # ── Panel derecho ─────────────────────────────────────────────────────────
    def _build_right(self, parent):
        res = tk.Frame(parent, bg=COLORS['bg_card'],
                       highlightbackground=COLORS['border'], highlightthickness=1)
        res.pack(fill='x', padx=6, pady=(0, 4))
        self._build_results(res)
        cf = tk.Frame(parent, bg=COLORS['bg'])
        cf.pack(fill='both', expand=True, padx=6, pady=4)
        self._cc_x = CollapsibleChart(cf, 'Carta X̄ – Media del Proceso', figsize=(9, 2.8))
        self._cc_x.pack(fill='both', expand=True, pady=(0, 2))
        self.ax_x = self._cc_x.ax
        self._cc_s = CollapsibleChart(cf, 'Carta S – Desviación Estándar', figsize=(9, 2.8))
        self._cc_s.pack(fill='both', expand=True, pady=(2, 0))
        self.ax_s = self._cc_s.ax
        self._draw_empty()

    def _build_results(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Límites de Control Calculados', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')
        body = tk.Frame(parent, bg=COLORS['bg_card']); body.pack(fill='x', padx=10, pady=8)
        self.result_labels = {}
        fields = [('X̄̄', 'xbar_bar'), ('S̄', 's_bar'), ('σ̂', 'sigma_est'),
                  ('LCS X̄', 'ucl_x'), ('LC X̄', 'cl_x'), ('LCI X̄', 'lcl_x'),
                  ('LCS S', 'ucl_s'), ('LC S', 'cl_s'), ('LCI S', 'lcl_s')]
        for i, (lbl, key) in enumerate(fields):
            r, c = divmod(i, 3)
            f = tk.Frame(body, bg=COLORS['bg_card'])
            f.grid(row=r, column=c, padx=10, pady=4, sticky='w')
            tk.Label(f, text=lbl+':', font=FONTS['label_b'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light'], width=8, anchor='e').pack(side='left')
            lb = tk.Label(f, text='—', font=FONTS['result'], bg=COLORS['bg_card'],
                          fg=COLORS['primary'], width=10, anchor='w')
            lb.pack(side='left')
            self.result_labels[key] = lb
        self.estado_lbl = tk.Label(body, text='', font=FONTS['subheader'],
                                   bg=COLORS['bg_card'], fg=COLORS['text'])
        self.estado_lbl.grid(row=3, column=0, columnspan=3, pady=(4, 0), sticky='w', padx=10)

    def _draw_empty(self):
        for ax, title in [(self.ax_x, 'Carta X̄ – Media del Proceso'),
                          (self.ax_s, 'Carta S – Desviación Estándar')]:
            ax.clear(); ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
            ax.tick_params(labelsize=8)
        self._cc_x.fig.tight_layout(pad=1.5); self._cc_x.draw()
        self._cc_s.fig.tight_layout(pad=1.5); self._cc_s.draw()

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _get_table_data(self):
        n = self.n_var.get(); data = []
        for row_ent in self._entry_cells:
            row = [parse_value(e.get()) for e in row_ent[:n]]
            if all(v is not None for v in row):
                data.append(row)
            elif any(v is not None for v in row):
                break
            else:
                break
        return data

    def _run(self):
        data = self._get_table_data()
        if len(data) < 2:
            messagebox.showwarning('Datos insuficientes', 'Ingrese al menos 2 subgrupos completos.'); return
        n = self.n_var.get()
        try:
            xbars, stds = compute_xbar_s(data)
            for i, (xb, s) in enumerate(zip(xbars, stds)):
                self._xbar_labels[i].configure(text=f'{xb:.4f}')
                self._s_labels[i].configure(text=f'{s:.4f}')
            lim = self._read_manual_limits()
            if lim is None:
                lim = compute_control_limits_xs(xbars, stds, n)
                self._fill_limits(lim); self._limits_cache = lim
            ooc_x = detect_out_of_control(xbars, lim['ucl_x'], lim['lcl_x'])
            ooc_s = detect_out_of_control(stds,  lim['ucl_s'], lim['lcl_s'])
            we    = western_electric_rules(xbars, lim['ucl_x'], lim['cl_x'], lim['lcl_x'])
            lie   = parse_value(self.spec_entries['lie'].get())
            lse   = parse_value(self.spec_entries['lse'].get())
            tgt   = parse_value(self.spec_entries['target'].get())
            self._update_results(lim, ooc_x, ooc_s, we)
            self._draw_charts(xbars, stds, lim, ooc_x, ooc_s, we, lie, lse, tgt)
        except Exception as ex:
            messagebox.showerror('Error de cálculo', str(ex))

    def _read_manual_limits(self):
        vals = {k: parse_value(self.lim_entries[k].get())
                for k in ['lc_x', 'ucs_x', 'lci_x', 'lc_s', 'ucs_s']}
        if all(v is not None for v in vals.values()):
            return {'xbar_bar': vals['lc_x'], 'cl_x': vals['lc_x'],
                    'ucl_x': vals['ucs_x'], 'lcl_x': vals['lci_x'],
                    'cl_s': vals['lc_s'],   'ucl_s': vals['ucs_s'],
                    'lcl_s': 0.0, 's_bar': vals['lc_s'], 'sigma_est': None}
        return None

    def _fill_limits(self, lim):
        for key, val in [('lc_x', lim['cl_x']), ('ucs_x', lim['ucl_x']),
                          ('lci_x', lim['lcl_x']), ('lc_s', lim['cl_s']),
                          ('ucs_s', lim['ucl_s'])]:
            e = self.lim_entries[key]; e.delete(0, 'end'); e.insert(0, f'{val:.5f}')

    def _update_results(self, lim, ooc_x, ooc_s, we):
        for key, val in [('xbar_bar', lim['xbar_bar']), ('s_bar', lim['s_bar']),
                          ('sigma_est', lim.get('sigma_est') or 0),
                          ('ucl_x', lim['ucl_x']), ('cl_x', lim['cl_x']),
                          ('lcl_x', lim['lcl_x']), ('ucl_s', lim['ucl_s']),
                          ('cl_s', lim['cl_s']), ('lcl_s', lim['lcl_s'])]:
            self.result_labels[key].configure(text=f'{val:.4f} lb' if val else '—')
        we_pts = set().union(*[set(we[k]) for k in range(2, 7) if we[k]])
        total = len(set(ooc_x)|set(ooc_s)|we_pts)
        if total == 0:
            self.estado_lbl.configure(text='✔ Proceso bajo control estadístico', fg=COLORS['success'])
        else:
            msg = f'✘ {len(set(ooc_x)|set(ooc_s))} fuera de límites'
            if we_pts: msg += f'  |  {len(we_pts)} violación(es) WE'
            self.estado_lbl.configure(text=msg, fg=COLORS['danger'])

    def _draw_charts(self, xbars, stds, lim, ooc_x, ooc_s, we, lie, lse, tgt):
        we_pts = set().union(*[set(we[k]) for k in range(2, 7) if we[k]])
        for ax, cc, vals, ucl, cl, lcl, ooc, ylabel, title, su, sl, tg, apply_we in [
            (self.ax_x, self._cc_x, xbars, lim['ucl_x'], lim['cl_x'], lim['lcl_x'],
             ooc_x, 'Media X̄ (lb)', 'Carta X̄ – Media del Proceso', lse, lie, tgt, True),
            (self.ax_s, self._cc_s, stds,  lim['ucl_s'], lim['cl_s'], lim['lcl_s'],
             ooc_s, 'S (lb)', 'Carta S – Desviación Estándar', None, None, None, False),
        ]:
            ax.clear(); ax.set_facecolor('#FAFAFA')
            sg = list(range(1, len(vals)+1))
            ax.axhline(ucl, color=COLORS['chart_ucl'], lw=1.5, ls='--', label=f'LCS={ucl:.4f}')
            ax.axhline(cl,  color=COLORS['chart_cl'],  lw=1.5, ls='-',  label=f'LC={cl:.4f}')
            ax.axhline(lcl, color=COLORS['chart_lcl'], lw=1.5, ls='--', label=f'LCI={lcl:.4f}')
            if su: ax.axhline(su, color=COLORS['chart_spec_u'], lw=1.0, ls=':', label=f'LSE={su:.3f}')
            if sl: ax.axhline(sl, color=COLORS['chart_spec_l'], lw=1.0, ls=':', label=f'LIE={sl:.3f}')
            if tg: ax.axhline(tg, color=COLORS['chart_target'], lw=1.0, ls='-.', label=f'Obj={tg:.3f}', alpha=0.7)
            ax.plot(sg, vals, color=COLORS['chart_data'], lw=1.2, marker='o', ms=4, zorder=3)
            for idx in ooc:
                ax.plot(sg[idx], vals[idx], 'o', color=COLORS['chart_out'], ms=8, zorder=5)
                ax.annotate(f'SG{sg[idx]}', (sg[idx], vals[idx]),
                            textcoords='offset points', xytext=(4, 4),
                            fontsize=7, color=COLORS['chart_out'])
            if apply_we:
                for idx in we_pts:
                    if idx not in ooc and idx < len(sg):
                        ax.plot(sg[idx], vals[idx], 'D', color=COLORS['warning'], ms=7, zorder=4)
            ax.set_xlabel('Subgrupo', fontsize=8); ax.set_ylabel(ylabel, fontsize=8)
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.set_xlim(0.5, len(sg)+0.5); ax.tick_params(labelsize=8)
            ax.legend(fontsize=7, loc='upper right', ncol=2)
            ax.grid(True, alpha=0.3, ls=':')
            cc.fig.tight_layout(pad=1.5); cc.draw()

    def _load_fase1(self): self._load_data(FASE_I_DATA)
    def _load_fase2(self): self._load_data(FASE_II_DATA)

    def _load_data(self, data):
        n = len(data[0]) if data else 6
        if self.n_var.get() != n:
            self.n_var.set(n); self._rebuild_table()
        self._clear_table(confirm=False)
        for i, row in enumerate(data[:MAX_SUBGROUPS]):
            for j, val in enumerate(row):
                if j < len(self._entry_cells[i]):
                    self._entry_cells[i][j].delete(0, 'end')
                    self._entry_cells[i][j].insert(0, str(val))

    def _clear_table(self, confirm=True):
        if confirm and not messagebox.askyesno('Confirmar', '¿Limpiar todos los datos?'):
            return
        for row in self._entry_cells:
            for e in row: e.delete(0, 'end')
        for lb in self._xbar_labels + self._s_labels:
            lb.configure(text='')
        for lb in self.result_labels.values():
            lb.configure(text='—')
        self.estado_lbl.configure(text='')
        for e in self.lim_entries.values():
            e.delete(0, 'end')
        self._draw_empty()
