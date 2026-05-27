# -*- coding: utf-8 -*-
"""
Módulo: Cartas de Control por Atributos  p · np · u
ControlMetrics
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS
from utils.spc_utils import (compute_p_chart, compute_np_chart, compute_u_chart,
                              detect_out_of_control, parse_value)
from utils.widgets import CollapsibleChart

MAX_ROWS = 60


class CartasPNPUModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._chart_type = tk.StringVar(value='p')
        self._build_ui()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Selector de tipo
        sel_f = tk.Frame(self, bg=COLORS['bg'], pady=6)
        sel_f.pack(fill='x', padx=16)
        tk.Label(sel_f, text='Tipo de carta:', font=FONTS['label_b'],
                 bg=COLORS['bg'], fg=COLORS['text']).pack(side='left', padx=(0, 8))
        chart_types = [
            ('p  – Proporción no conforme (n variable)',   'p'),
            ('np – Número no conforme (n constante)',       'np'),
            ('u  – Defectos por unidad (n variable)',       'u'),
        ]
        for txt, val in chart_types:
            tk.Radiobutton(sel_f, text=txt, variable=self._chart_type, value=val,
                           bg=COLORS['bg'], fg=COLORS['text'], font=FONTS['label'],
                           activebackground=COLORS['bg'], selectcolor=COLORS['bg_card'],
                           command=self._on_type_change).pack(side='left', padx=6)

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=6, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=360, width=400)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=460)
        self._build_right(right)

    def _on_type_change(self):
        self._update_headers()
        self._clear_table(confirm=False)

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

        # Cabecera dinámica
        self._hdr_lbl_frame = tk.Frame(parent, bg=COLORS['primary_light'], pady=6)
        self._hdr_lbl_frame.pack(fill='x')
        self._hdr_lbl = tk.Label(self._hdr_lbl_frame, text='Datos – Carta p',
                                  font=FONTS['subheader'], bg=COLORS['primary_light'],
                                  fg=COLORS['text_white'])
        self._hdr_lbl.pack(padx=12, side='left')

        # n constante (solo carta np)
        self._n_frame = tk.Frame(parent, bg=COLORS['bg_card'], pady=4)
        self._n_frame.pack(fill='x', padx=10)
        tk.Label(self._n_frame, text='Tamaño de muestra n (constante):',
                 font=FONTS['label_b'], bg=COLORS['bg_card'],
                 fg=COLORS['text']).pack(side='left', padx=(0, 6))
        self._n_const = tk.Entry(self._n_frame, width=7, font=FONTS['entry'],
                                  bd=1, relief='solid')
        self._n_const.insert(0, '50')
        self._n_const.pack(side='left')
        self._n_frame.pack_forget()   # hidden by default (shown only for np)

        # Tabla de datos
        tbl_hdr = tk.Frame(parent, bg=COLORS['primary'], pady=3)
        tbl_hdr.pack(fill='x', padx=10, pady=(6, 0))
        self._tbl_hdr_frame = tbl_hdr
        tk.Button(tbl_hdr, text='✕ Limpiar', command=self._clear_table,
                  bg=COLORS['primary'], fg='#FFCDD2', font=FONTS['small'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=2).pack(side='right', padx=6)
        self._tbl_collapsed = False
        self._tbl_toggle_btn = tk.Button(tbl_hdr, text='▲', command=self._toggle_table,
                  bg=COLORS['primary'], fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=6, pady=0)
        self._tbl_toggle_btn.pack(side='left', padx=(6, 2))
        self._tbl_title = tk.Label(tbl_hdr, text='Tabla de Datos',
                 font=FONTS['label_b'], bg=COLORS['primary'],
                 fg=COLORS['text_white'])
        self._tbl_title.pack(side='left', padx=(0, 6))

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
        bf.pack(fill='x', padx=10, pady=(4, 8))
        for txt, cmd, bg, fg in [
                ('Calcular carta', self._run, COLORS['primary'], COLORS['text_white']),
                ('Limpiar tabla',  self._clear_table, '#CFD8DC', COLORS['text'])]:
            tk.Button(bf, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

    def _build_data_table(self):
        for w in self.tbl_inner.winfo_children():
            w.destroy()
        self._count_entries = []
        self._n_entries     = []
        self._rate_labels   = []

        ct = self._chart_type.get()
        if ct == 'p':
            h2, h3 = 'Def.', 'n'
        elif ct == 'np':
            h2, h3 = 'Def.', '—'
        else:
            h2, h3 = 'Def.', 'n'

        for j, (h, w, bg) in enumerate(zip(
                ['Muestra', h2, h3, 'Tasa'],
                [6, 7, 7, 8],
                [COLORS['primary'], COLORS['primary_light'],
                 COLORS['primary_light'], COLORS['bg_subheader']])):
            tk.Label(self.tbl_inner, text=h, font=FONTS['label_b'], bg=bg,
                     fg=COLORS['text_white'], width=w, pady=4).grid(
                         row=0, column=j, padx=1, pady=1, sticky='ew')

        for i in range(MAX_ROWS):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            tk.Label(self.tbl_inner, text=str(i+1), font=FONTS['small'],
                     bg=COLORS['primary_lighter'], fg=COLORS['text_white'], width=6).grid(
                         row=i+1, column=0, padx=1, pady=1)
            ec = tk.Entry(self.tbl_inner, width=7, font=FONTS['entry'],
                          bd=0, relief='flat', bg=bg,
                          highlightbackground=COLORS['border'], highlightthickness=1)
            ec.grid(row=i+1, column=1, padx=1, pady=1)
            self._count_entries.append(ec)

            if ct != 'np':
                en = tk.Entry(self.tbl_inner, width=7, font=FONTS['entry'],
                              bd=0, relief='flat', bg=bg,
                              highlightbackground=COLORS['border'], highlightthickness=1)
                en.grid(row=i+1, column=2, padx=1, pady=1)
                self._n_entries.append(en)
            else:
                tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                         bg=bg, width=7).grid(row=i+1, column=2, padx=1, pady=1)
                self._n_entries.append(None)

            rl = tk.Label(self.tbl_inner, text='', font=FONTS['small'],
                          bg='#E8F5E9', fg=COLORS['text'], width=8)
            rl.grid(row=i+1, column=3, padx=1, pady=1)
            self._rate_labels.append(rl)

    def _update_headers(self):
        ct = self._chart_type.get()
        titles = {'p': 'Datos – Carta p (Proporción no conforme)',
                  'np': 'Datos – Carta np (Número no conforme)',
                  'u':  'Datos – Carta u (Defectos por unidad)'}
        self._hdr_lbl.configure(text=titles[ct])
        if ct == 'np':
            self._n_frame.pack(fill='x', padx=10, pady=(4, 0))
        else:
            self._n_frame.pack_forget()
        self._build_data_table()

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
        self._cc = CollapsibleChart(cf, 'Carta de Atributos', figsize=(9, 4))
        self._cc.pack(fill='both', expand=True)
        self.ax = self._cc.ax
        self._draw_empty()

    def _build_results(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Resultados', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')
        body = tk.Frame(parent, bg=COLORS['bg_card']); body.pack(fill='x', padx=10, pady=8)
        self.result_labels = {}
        for i, (lbl, key) in enumerate([('Parámetro central', 'center'),
                                          ('LCS', 'ucl'), ('LCI', 'lcl'),
                                          ('N° muestras', 'n_samples'),
                                          ('Fuera de control', 'ooc')]):
            f = tk.Frame(body, bg=COLORS['bg_card'])
            f.grid(row=0, column=i, padx=8, pady=4, sticky='w')
            tk.Label(f, text=lbl+':', font=FONTS['label_b'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light'], anchor='e').pack(side='left', padx=(0, 4))
            lb = tk.Label(f, text='—', font=FONTS['result'], bg=COLORS['bg_card'],
                          fg=COLORS['primary'], width=8, anchor='w')
            lb.pack(side='left'); self.result_labels[key] = lb
        self.estado_lbl = tk.Label(body, text='', font=FONTS['subheader'],
                                   bg=COLORS['bg_card'], fg=COLORS['text'])
        self.estado_lbl.grid(row=1, column=0, columnspan=5, pady=(2, 0), sticky='w', padx=8)

    def _draw_empty(self):
        ax = self.ax; ax.clear(); ax.set_facecolor('#FAFAFA')
        ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
        ax.tick_params(labelsize=8)
        self._cc.fig.tight_layout(pad=1.5); self._cc.draw()

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _get_data(self):
        ct = self._chart_type.get()
        counts, ns = [], []
        for i, ec in enumerate(self._count_entries):
            c = parse_value(ec.get())
            if c is None: break
            counts.append(c)
            if ct == 'np':
                ns.append(None)
            else:
                n = parse_value(self._n_entries[i].get()) if self._n_entries[i] else None
                if n is None: break
                ns.append(n)
        return counts, ns

    def _run(self):
        ct = self._chart_type.get()
        counts, ns = self._get_data()
        if len(counts) < 3:
            messagebox.showwarning('Datos insuficientes', 'Ingrese al menos 3 muestras.'); return
        try:
            if ct == 'np':
                n_val = parse_value(self._n_const.get())
                if n_val is None or n_val <= 0:
                    messagebox.showwarning('n inválido', 'Ingrese un tamaño de muestra n > 0.'); return
                res = compute_np_chart(counts, int(n_val))
                values = res['np_values']
                ucl_v  = [res['ucl_np']] * len(values)
                lcl_v  = [res['lcl_np']] * len(values)
                cl_v   = res['cl_np']
                label  = 'Número no conforme (np)'
                c_txt  = f"np̄ = {res['np_bar']:.4f}  (p̄ = {res['p_bar']:.4f})"
                for i, v in enumerate(values):
                    self._rate_labels[i].configure(text=f'{v:.1f}')
            elif ct == 'p':
                res = compute_p_chart(counts, ns)
                values = res['p_values']
                ucl_v  = res['ucl_p']
                lcl_v  = res['lcl_p']
                cl_v   = res['p_bar']
                label  = 'Proporción no conforme (p)'
                c_txt  = f"p̄ = {res['p_bar']:.4f}"
                for i, v in enumerate(values):
                    self._rate_labels[i].configure(text=f'{v:.4f}')
            else:  # u
                res = compute_u_chart(counts, ns)
                values = res['u_values']
                ucl_v  = res['ucl_u']
                lcl_v  = res['lcl_u']
                cl_v   = res['u_bar']
                label  = 'Defectos por unidad (u)'
                c_txt  = f"ū = {res['u_bar']:.4f}"
                for i, v in enumerate(values):
                    self._rate_labels[i].configure(text=f'{v:.4f}')

            # Fuera de control (compara contra límite promedio si variable)
            ucl_avg = float(np.mean(ucl_v))
            lcl_avg = float(np.mean(lcl_v))
            ooc = [i for i, (v, u, l) in enumerate(
                zip(values, ucl_v if isinstance(ucl_v, list) else [ucl_v]*len(values),
                            lcl_v if isinstance(lcl_v, list) else [lcl_v]*len(values)))
                   if v > u or v < l]

            self.result_labels['center'].configure(text=c_txt)
            self.result_labels['ucl'].configure(text=f'{ucl_avg:.4f}')
            self.result_labels['lcl'].configure(text=f'{lcl_avg:.4f}')
            self.result_labels['n_samples'].configure(text=str(len(values)))
            self.result_labels['ooc'].configure(text=str(len(ooc)))
            if len(ooc) == 0:
                self.estado_lbl.configure(text='✔ Proceso bajo control estadístico', fg=COLORS['success'])
            else:
                self.estado_lbl.configure(text=f'✘ {len(ooc)} punto(s) fuera de control', fg=COLORS['danger'])

            self._draw_chart(values, ucl_v, cl_v, lcl_v, ooc, label, ct)
        except Exception as ex:
            messagebox.showerror('Error de cálculo', str(ex))

    def _draw_chart(self, values, ucl_v, cl_v, lcl_v, ooc, ylabel, ct):
        ax = self.ax; ax.clear(); ax.set_facecolor('#FAFAFA')
        sg = list(range(1, len(values)+1))
        titles = {'p': 'Carta p – Proporción No Conforme',
                  'np': 'Carta np – Número No Conforme',
                  'u': 'Carta u – Defectos por Unidad'}

        if isinstance(ucl_v, list):
            ax.plot(sg, ucl_v, color=COLORS['chart_ucl'], lw=1.5, ls='--', label='LCS')
            ax.plot(sg, lcl_v, color=COLORS['chart_lcl'], lw=1.5, ls='--', label='LCI')
        else:
            ax.axhline(ucl_v, color=COLORS['chart_ucl'], lw=1.5, ls='--', label=f'LCS={ucl_v:.4f}')
            ax.axhline(lcl_v, color=COLORS['chart_lcl'], lw=1.5, ls='--', label=f'LCI={lcl_v:.4f}')
        ax.axhline(cl_v, color=COLORS['chart_cl'], lw=1.5, ls='-', label=f'LC={cl_v:.4f}')
        ax.plot(sg, values, color=COLORS['chart_data'], lw=1.2, marker='o', ms=5, zorder=3)
        for idx in ooc:
            ax.plot(sg[idx], values[idx], 'o', color=COLORS['chart_out'], ms=9, zorder=5)
            ax.annotate(str(sg[idx]), (sg[idx], values[idx]),
                        textcoords='offset points', xytext=(4, 4),
                        fontsize=7, color=COLORS['chart_out'])
        ax.set_xlabel('Muestra', fontsize=8); ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(titles[ct], fontsize=10, fontweight='bold', color=COLORS['text'])
        ax.set_xlim(0.5, len(sg)+0.5); ax.tick_params(labelsize=8)
        ax.legend(fontsize=7, loc='upper right'); ax.grid(True, alpha=0.3, ls=':')
        self._cc.fig.tight_layout(pad=1.5); self._cc.draw()

    def _clear_table(self, confirm=True):
        if confirm and not messagebox.askyesno('Confirmar', '¿Limpiar todos los datos?'):
            return
        for e in self._count_entries: e.delete(0, 'end')
        for e in self._n_entries:
            if e: e.delete(0, 'end')
        for lb in self._rate_labels: lb.configure(text='')
        for lb in self.result_labels.values(): lb.configure(text='—')
        self.estado_lbl.configure(text='')
        self._draw_empty()
