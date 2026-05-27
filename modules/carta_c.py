# -*- coding: utf-8 -*-
"""
Módulo: Carta C – Defectos por Unidad + Diagrama de Pareto
Sistema SPC – PMD y Cía S.C.A.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, CARTA_C_DATA, DEFECTOS_DATA, DEFAULTS
from utils.spc_utils import compute_control_limits_c, detect_out_of_control, parse_value
from utils.widgets import CollapsibleChart

MAX_CAJAS = 60
MAX_DEFECT_TYPES = 20


class CartaCModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._build_ui()

    def _build_ui(self):
        inst = tk.Label(self, text=(
            "Ingrese el número de defectos leves por caja (Carta C) y los tipos de defecto "
            "para el diagrama de Pareto. Criterio de aceptación: ≤ 2 defectos leves por caja."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=900, justify='left')
        inst.pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'], sashwidth=6)
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=320, width=360)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=500)
        self._build_right(right)

    # ── Panel izquierdo ───────────────────────────────────────────────────────
    def _build_left(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Datos de Entrada', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        # Criterio de aceptación
        cfg_f = tk.Frame(parent, bg=COLORS['bg_card'])
        cfg_f.pack(fill='x', padx=10, pady=(6, 2))
        tk.Label(cfg_f, text='Criterio de aceptación (máx. defectos leves/caja):',
                 font=FONTS['small'], bg=COLORS['bg_card'], fg=COLORS['text_light']).pack(side='left')
        self.acept_var = tk.StringVar(value='2')
        ttk.Spinbox(cfg_f, from_=0, to=20, textvariable=self.acept_var,
                    width=5, state='readonly').pack(side='left', padx=6)

        # Tabla de defectos por caja
        tbl_hdr = tk.Frame(parent, bg=COLORS['primary'], pady=3)
        tbl_hdr.pack(fill='x', padx=10, pady=(4, 0))
        tk.Label(tbl_hdr, text='Defectos por Caja (Carta C)',
                 font=FONTS['label_b'], bg=COLORS['primary'],
                 fg=COLORS['text_white']).pack(side='left', padx=10)

        outer_c = tk.Frame(parent, bg=COLORS['border'], bd=1)
        outer_c.pack(fill='x', padx=10, pady=(0, 4), ipady=0)

        c_canvas = tk.Canvas(outer_c, bg=COLORS['bg_card'], height=150, highlightthickness=0)
        vsb_c = ttk.Scrollbar(outer_c, orient='vertical', command=c_canvas.yview)
        c_canvas.configure(yscrollcommand=vsb_c.set)
        vsb_c.pack(side='right', fill='y')
        c_canvas.pack(side='left', fill='x', expand=True)

        inner_c = tk.Frame(c_canvas, bg=COLORS['bg_card'])
        c_canvas.create_window((0, 0), window=inner_c, anchor='nw')
        inner_c.bind('<Configure>', lambda e: c_canvas.configure(
            scrollregion=c_canvas.bbox('all')))

        # Encabezado
        for j, (h, w) in enumerate([('Caja #', 6), ('Defectos leves', 14), ('Conforme', 10)]):
            tk.Label(inner_c, text=h, font=FONTS['label_b'],
                     bg=COLORS['primary'], fg=COLORS['text_white'], width=w, pady=3).grid(
                         row=0, column=j, padx=1, pady=1)

        self.caja_entries = []
        self.conformidad_labels = []
        for i in range(MAX_CAJAS):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            tk.Label(inner_c, text=str(i+1), font=FONTS['small'],
                     bg=COLORS['primary_lighter'], fg=COLORS['text_white'], width=6).grid(
                         row=i+1, column=0, padx=1, pady=1)
            e = tk.Entry(inner_c, width=14, font=FONTS['entry'], bd=0,
                         relief='flat', bg=bg,
                         highlightbackground=COLORS['border'], highlightthickness=1)
            e.grid(row=i+1, column=1, padx=1, pady=1)
            self.caja_entries.append(e)
            lbl = tk.Label(inner_c, text='', font=FONTS['small'], bg=bg, fg=COLORS['text'], width=10)
            lbl.grid(row=i+1, column=2, padx=1, pady=1)
            self.conformidad_labels.append(lbl)

        # Tabla de tipos de defecto (para Pareto)
        tbl_hdr2 = tk.Frame(parent, bg=COLORS['primary'], pady=3)
        tbl_hdr2.pack(fill='x', padx=10, pady=(6, 0))
        tk.Label(tbl_hdr2, text='Tipos de Defecto (Diagrama de Pareto)',
                 font=FONTS['label_b'], bg=COLORS['primary'],
                 fg=COLORS['text_white']).pack(side='left', padx=10)

        outer_p = tk.Frame(parent, bg=COLORS['border'], bd=1)
        outer_p.pack(fill='x', padx=10, pady=(0, 4))

        p_canvas = tk.Canvas(outer_p, bg=COLORS['bg_card'], height=120, highlightthickness=0)
        vsb_p = ttk.Scrollbar(outer_p, orient='vertical', command=p_canvas.yview)
        p_canvas.configure(yscrollcommand=vsb_p.set)
        vsb_p.pack(side='right', fill='y')
        p_canvas.pack(side='left', fill='both', expand=True)

        inner_p = tk.Frame(p_canvas, bg=COLORS['bg_card'])
        p_canvas.create_window((0, 0), window=inner_p, anchor='nw')
        inner_p.bind('<Configure>', lambda e: p_canvas.configure(
            scrollregion=p_canvas.bbox('all')))

        for j, (h, w) in enumerate([('Tipo de Defecto', 18), ('Frecuencia', 10)]):
            tk.Label(inner_p, text=h, font=FONTS['label_b'],
                     bg=COLORS['primary'], fg=COLORS['text_white'], width=w, pady=3).grid(
                         row=0, column=j, padx=1, pady=1)

        self.defect_type_entries = []
        self.defect_freq_entries = []
        for i in range(MAX_DEFECT_TYPES):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            et = tk.Entry(inner_p, width=18, font=FONTS['entry'], bd=0, relief='flat',
                          bg=bg, highlightbackground=COLORS['border'], highlightthickness=1)
            et.grid(row=i+1, column=0, padx=1, pady=1)
            ef = tk.Entry(inner_p, width=10, font=FONTS['entry'], bd=0, relief='flat',
                          bg=bg, highlightbackground=COLORS['border'], highlightthickness=1)
            ef.grid(row=i+1, column=1, padx=1, pady=1)
            self.defect_type_entries.append(et)
            self.defect_freq_entries.append(ef)

        # Botones
        btn_f = tk.Frame(parent, bg=COLORS['bg_card'])
        btn_f.pack(fill='x', padx=10, pady=(4, 4))
        btns = [
            ('Calcular', self._run, COLORS['primary'], COLORS['text_white']),
            ('Datos del estudio', self._load_demo, COLORS['secondary'], COLORS['text']),
            ('Limpiar', self._clear, '#CFD8DC', COLORS['text']),
        ]
        for txt, cmd, bg, fg in btns:
            tk.Button(btn_f, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Sección Excel
        excel_sep = tk.Frame(parent, bg=COLORS['bg_card'])
        excel_sep.pack(fill='x', padx=10, pady=(0, 8))
        tk.Frame(excel_sep, bg=COLORS['border'], height=1).pack(fill='x', pady=(0, 3))
        tk.Label(excel_sep,
                 text='📋 Excel: Hoja 1 "CartaC" col. A = defectos/caja  |  Hoja 2 "Pareto" col. A = tipo, col. B = frecuencia',
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['text_light'], wraplength=340, justify='left').pack(anchor='w')
        excel_btns = tk.Frame(excel_sep, bg=COLORS['bg_card'])
        excel_btns.pack(fill='x', pady=2)
        tk.Button(excel_btns, text='📂 Cargar desde Excel', command=self._load_excel,
                  bg='#0277BD', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)
        tk.Button(excel_btns, text='📄 Plantilla Excel', command=self._gen_template,
                  bg='#37474F', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

    # ── Panel derecho ─────────────────────────────────────────────────────────
    def _build_right(self, parent):
        res = tk.Frame(parent, bg=COLORS['bg_card'],
                       highlightbackground=COLORS['border'], highlightthickness=1)
        res.pack(fill='x', padx=6, pady=(0, 4))
        self._build_results(res)

        chart_f = tk.Frame(parent, bg=COLORS['bg'])
        chart_f.pack(fill='both', expand=True, padx=6, pady=4)
        self._build_charts(chart_f)

    def _build_results(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Resultados – Carta C', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)

        self.res_labels = {}
        fields = [
            ('Cajas inspeccionadas:', 'n_cajas'),
            ('C̄ (defectos/caja):', 'c_bar'),
            ('LCS:', 'ucl'),
            ('LCI:', 'lcl'),
            ('Cajas no conformes:', 'nc_cajas'),
        ]
        for i, (lbl, key) in enumerate(fields):
            r, c = divmod(i, 3)
            f = tk.Frame(body, bg=COLORS['bg_card'])
            f.grid(row=r, column=c, padx=12, pady=4, sticky='w')
            tk.Label(f, text=lbl, font=FONTS['label_b'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light'], anchor='e').pack(side='left')
            lb = tk.Label(f, text='—', font=FONTS['result'],
                          bg=COLORS['bg_card'], fg=COLORS['primary'], width=12, anchor='w')
            lb.pack(side='left', padx=4)
            self.res_labels[key] = lb

        self.estado_c = tk.Label(body, text='', font=FONTS['subheader'],
                                 bg=COLORS['bg_card'], fg=COLORS['text'])
        self.estado_c.grid(row=2, column=0, columnspan=3, sticky='w', padx=12, pady=(4, 0))

    def _build_charts(self, parent):
        self._cc_c = CollapsibleChart(
            parent, 'Carta C – Defectos por Caja', figsize=(6, 3.5))
        self._cc_c.pack(side='left', fill='both', expand=True, padx=(0, 2))
        self.ax_c = self._cc_c.ax

        self._cc_pareto = CollapsibleChart(
            parent, 'Diagrama de Pareto – Tipos de Defecto', figsize=(6, 3.5))
        self._cc_pareto.pack(side='left', fill='both', expand=True, padx=(2, 0))
        self.ax_pareto = self._cc_pareto.ax

        self._draw_empty()

    def _draw_all(self):
        self._cc_c.fig.tight_layout(pad=1.5)
        self._cc_pareto.fig.tight_layout(pad=1.5)
        self._cc_c.draw()
        self._cc_pareto.draw()

    def _draw_empty(self):
        for ax, title in [(self.ax_c, 'Carta C – Defectos por Caja'),
                          (self.ax_pareto, 'Diagrama de Pareto – Tipos de Defecto')]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
        self._draw_all()

    # ── Lógica ───────────────────────────────────────────────────────────────
    def _get_caja_data(self):
        defects = []
        for e in self.caja_entries:
            val = parse_value(e.get())
            if val is not None:
                defects.append(int(round(val)))
            elif e.get().strip() == '':
                break
        return defects

    def _get_pareto_data(self):
        tipos = {}
        for et, ef in zip(self.defect_type_entries, self.defect_freq_entries):
            name = et.get().strip()
            freq_val = parse_value(ef.get())
            if name and freq_val is not None:
                tipos[name] = int(round(freq_val))
        return tipos

    def _run(self):
        defects = self._get_caja_data()
        if len(defects) < 2:
            messagebox.showwarning('Datos insuficientes',
                                   'Ingrese al menos 2 valores de defectos por caja.')
            return
        try:
            acept = int(self.acept_var.get())
            lim = compute_control_limits_c(defects)
            ooc = detect_out_of_control(defects, lim['ucl'], lim['lcl'])
            nc = sum(1 for d in defects if d > acept)

            # Actualizar conformidad
            for i, d in enumerate(defects):
                conforme = d <= acept
                self.conformidad_labels[i].configure(
                    text='✔ Sí' if conforme else '✘ No',
                    fg=COLORS['success'] if conforme else COLORS['danger'])

            self._update_results(lim, defects, ooc, nc)

            tipos = self._get_pareto_data()
            self._draw_charts(defects, lim, ooc, tipos, acept)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _update_results(self, lim, defects, ooc, nc):
        self.res_labels['n_cajas'].configure(text=str(len(defects)))
        self.res_labels['c_bar'].configure(text=f"{lim['c_bar']:.4f}")
        self.res_labels['ucl'].configure(text=f"{lim['ucl']:.4f}")
        self.res_labels['lcl'].configure(text=f"{lim['lcl']:.4f}")
        self.res_labels['nc_cajas'].configure(
            text=f"{nc} ({nc/len(defects)*100:.1f}%)",
            fg=COLORS['danger'] if nc > 0 else COLORS['success'])

        if len(ooc) == 0:
            self.estado_c.configure(
                text='✔ Proceso bajo control estadístico (Carta C)',
                fg=COLORS['success'])
        else:
            self.estado_c.configure(
                text=f'✘ {len(ooc)} punto(s) fuera de control',
                fg=COLORS['danger'])

    def _draw_charts(self, defects, lim, ooc, tipos, acept):
        cajas = list(range(1, len(defects)+1))

        # ── Carta C ──
        ax = self.ax_c
        ax.clear()
        ax.set_facecolor('#FAFAFA')
        ax.axhline(lim['ucl'], color=COLORS['chart_ucl'], linewidth=1.5, linestyle='--',
                   label=f"LCS = {lim['ucl']:.3f}")
        ax.axhline(lim['c_bar'], color=COLORS['chart_cl'], linewidth=1.5, linestyle='-',
                   label=f"C̄  = {lim['c_bar']:.3f}")
        ax.axhline(lim['lcl'], color=COLORS['chart_lcl'], linewidth=1.5, linestyle='--',
                   label=f"LCI = {lim['lcl']:.3f}")
        ax.axhline(acept, color=COLORS['accent'], linewidth=1.2, linestyle=':',
                   label=f'Criterio accept. = {acept}', alpha=0.8)

        ax.plot(cajas, defects, color=COLORS['chart_data'], linewidth=1.2,
                marker='o', markersize=5, zorder=3)
        for idx in ooc:
            ax.plot(cajas[idx], defects[idx], 'o', color=COLORS['chart_out'],
                    markersize=9, zorder=4)
            ax.annotate(f'C{cajas[idx]}', (cajas[idx], defects[idx]),
                        textcoords='offset points', xytext=(4, 4),
                        fontsize=7, color=COLORS['chart_out'])

        ax.set_xlabel('Número de Caja', fontsize=9)
        ax.set_ylabel('Defectos leves', fontsize=9)
        ax.set_title('Carta C – Defectos por Caja', fontsize=10, fontweight='bold')
        ax.set_xlim(0.5, len(cajas)+0.5)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.legend(fontsize=7, loc='upper right')
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.tick_params(labelsize=8)

        # ── Pareto ──
        ax2 = self.ax_pareto
        ax2.clear()
        ax2.set_facecolor('#FAFAFA')

        if tipos:
            sorted_tipos = sorted(tipos.items(), key=lambda x: x[1], reverse=True)
            names  = [t[0] for t in sorted_tipos]
            freqs  = [t[1] for t in sorted_tipos]
            total  = sum(freqs)
            cumulative = np.cumsum(freqs) / total * 100

            colors_bars = [COLORS['primary_lighter']]*len(names)
            bars = ax2.bar(range(len(names)), freqs, color=colors_bars, edgecolor='white',
                           linewidth=0.8)
            ax2.set_xticks(range(len(names)))
            ax2.set_xticklabels(names, rotation=30, ha='right', fontsize=7)

            ax3 = ax2.twinx()
            ax3.plot(range(len(names)), cumulative, 'o-', color=COLORS['danger'],
                     linewidth=1.5, markersize=5, label='% Acumulado')
            ax3.axhline(80, color=COLORS['accent'], linewidth=1.0, linestyle='--', alpha=0.7, label='80%')
            ax3.set_ylim(0, 115)
            ax3.set_ylabel('% Acumulado', fontsize=8)
            ax3.tick_params(labelsize=7)
            ax3.legend(fontsize=7, loc='lower right')

            for bar, val in zip(bars, freqs):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                         str(val), ha='center', va='bottom', fontsize=7, fontweight='bold')

            ax2.set_ylabel('Frecuencia', fontsize=8)
            ax2.tick_params(labelsize=8)

        ax2.set_title('Diagrama de Pareto – Tipos de Defecto', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle=':', axis='y')

        self._draw_all()

    def _load_excel(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_read_defects
        fp = filedialog.askopenfilename(
            title='Seleccionar archivo Excel – Carta C / Pareto',
            filetypes=[('Excel', '*.xlsx *.xls'), ('Todos', '*.*')])
        if not fp:
            return
        try:
            result = excel_read_defects(fp)
            cajas = result['cajas']
            tipos = result['tipos']

            if not cajas and not tipos:
                messagebox.showwarning('Sin datos',
                    'No se encontraron datos en el archivo.\n'
                    'Revise que la Hoja 1 tenga defectos por caja en columna A '
                    'y la Hoja 2 (opcional) tenga tipos y frecuencias.')
                return

            if cajas:
                for e in self.caja_entries:
                    e.delete(0, 'end')
                for i, val in enumerate(cajas):
                    if i < MAX_CAJAS:
                        self.caja_entries[i].insert(0, str(val))

            if tipos:
                for et, ef in zip(self.defect_type_entries, self.defect_freq_entries):
                    et.delete(0, 'end')
                    ef.delete(0, 'end')
                for i, (name, freq) in enumerate(tipos.items()):
                    if i < MAX_DEFECT_TYPES:
                        self.defect_type_entries[i].insert(0, name)
                        self.defect_freq_entries[i].insert(0, str(freq))

            msg = []
            if cajas:  msg.append(f'{len(cajas)} cajas (Carta C)')
            if tipos:  msg.append(f'{len(tipos)} tipos de defecto (Pareto)')
            messagebox.showinfo('Excel cargado', 'Datos cargados:\n• ' + '\n• '.join(msg))
        except Exception as e:
            messagebox.showerror('Error al leer Excel', str(e))

    def _gen_template(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_create_template
        fp = filedialog.asksaveasfilename(
            title='Guardar plantilla Excel',
            defaultextension='.xlsx',
            initialfile='Plantilla_CartaC.xlsx',
            filetypes=[('Excel', '*.xlsx')])
        if not fp:
            return
        try:
            excel_create_template(fp, 'defects')
            messagebox.showinfo('Plantilla creada',
                f'Plantilla guardada en:\n{fp}\n\n'
                'Hoja 1 "CartaC": col. A = defectos por caja.\n'
                'Hoja 2 "Pareto": col. A = tipo, col. B = frecuencia.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _load_demo(self):
        # Carta C
        for i, e in enumerate(self.caja_entries):
            e.delete(0, 'end')
        for i, val in enumerate(CARTA_C_DATA):
            self.caja_entries[i].delete(0, 'end')
            self.caja_entries[i].insert(0, str(val))

        # Pareto
        for et, ef in zip(self.defect_type_entries, self.defect_freq_entries):
            et.delete(0, 'end')
            ef.delete(0, 'end')
        for i, (name, freq) in enumerate(DEFECTOS_DATA.items()):
            if i < MAX_DEFECT_TYPES:
                self.defect_type_entries[i].insert(0, name)
                self.defect_freq_entries[i].insert(0, str(freq))

    def _clear(self):
        for e in self.caja_entries:
            e.delete(0, 'end')
        for lbl in self.conformidad_labels:
            lbl.configure(text='')
        for et, ef in zip(self.defect_type_entries, self.defect_freq_entries):
            et.delete(0, 'end')
            ef.delete(0, 'end')
        for lb in self.res_labels.values():
            lb.configure(text='—', fg=COLORS['primary'])
        self.estado_c.configure(text='')
        self._draw_empty()


import matplotlib.ticker
