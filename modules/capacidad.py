# -*- coding: utf-8 -*-
"""
Módulo: Análisis de Capacidad del Proceso (Cp, Cpk)
Sistema SPC – PMD y Cía S.C.A.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS, FASE_I_DATA, SPC_CONSTANTS
from utils.spc_utils import compute_capability, parse_value, summary_stats
from utils.widgets import CollapsibleChart


class CapacidadModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._build_ui()

    def _build_ui(self):
        inst = tk.Label(self, text=(
            "Ingrese los datos de peso y los límites de especificación del cliente "
            "para calcular los índices de capacidad Cp y Cpk."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=900, justify='left')
        inst.pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'], sashwidth=6)
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=280, width=320)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=520)
        self._build_right(right)

    # ── Panel izquierdo ───────────────────────────────────────────────────────
    def _build_left(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Parámetros de Análisis', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)

        # Especificaciones
        spec = tk.LabelFrame(body, text='Especificaciones', bg=COLORS['bg_card'],
                             fg=COLORS['text'], font=FONTS['label_b'])
        spec.pack(fill='x', pady=(0, 8))

        spec_fields = [
            ('LIE – Cliente (lb):', 'lie', DEFAULTS['lie_cliente']),
            ('LSE – Cliente (lb):', 'lse', DEFAULTS['lse_cliente']),
            ('LIE – Interno (lb):', 'lie_i', DEFAULTS['lie_interno']),
            ('LSE – Interno (lb):', 'lse_i', DEFAULTS['lse_interno']),
            ('Valor Objetivo (lb):', 'target', DEFAULTS['target']),
        ]
        self.spec_entries = {}
        for i, (lbl, key, val) in enumerate(spec_fields):
            tk.Label(spec, text=lbl, font=FONTS['label_b'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light'], anchor='e', width=22).grid(
                         row=i, column=0, sticky='e', padx=(8, 4), pady=3)
            e = tk.Entry(spec, width=10, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, str(val))
            e.grid(row=i, column=1, sticky='w', padx=(0, 8), pady=3)
            self.spec_entries[key] = e

        # Fuente del sigma
        sigma_f = tk.LabelFrame(body, text='Fuente de σ (desviación estándar)',
                                bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['label_b'])
        sigma_f.pack(fill='x', pady=(0, 8))

        self.sigma_source = tk.StringVar(value='datos')
        tk.Radiobutton(sigma_f, text='Calcular desde los datos (σ muestral)',
                       variable=self.sigma_source, value='datos',
                       bg=COLORS['bg_card'], font=FONTS['small'],
                       command=self._toggle_sigma).pack(anchor='w', padx=8, pady=2)
        tk.Radiobutton(sigma_f, text='Ingresado manualmente (desde Carta R)',
                       variable=self.sigma_source, value='manual',
                       bg=COLORS['bg_card'], font=FONTS['small'],
                       command=self._toggle_sigma).pack(anchor='w', padx=8, pady=2)

        sf2 = tk.Frame(sigma_f, bg=COLORS['bg_card'])
        sf2.pack(fill='x', padx=8, pady=(2, 6))
        tk.Label(sf2, text='σ manual (lb):', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text_light']).pack(side='left')
        self.sigma_entry = tk.Entry(sf2, width=10, font=FONTS['entry'], bd=1, relief='solid',
                                    state='disabled')
        self.sigma_entry.pack(side='left', padx=6)
        self.sigma_entry.insert(0, '0.09865')

        # Datos
        tk.Label(body, text='Datos de Peso (lb) – uno por línea:',
                 font=FONTS['label_b'], bg=COLORS['bg_card'], fg=COLORS['text']).pack(
                     anchor='w', pady=(4, 2))
        txt_f = tk.Frame(body, bg=COLORS['border'], bd=1)
        txt_f.pack(fill='x', pady=4)
        self.txt_data = tk.Text(txt_f, font=FONTS['entry'], width=22, height=9,
                                bd=0, padx=6, pady=6, wrap='none', relief='flat',
                                bg=COLORS['bg_card'])
        sb = ttk.Scrollbar(txt_f, orient='vertical', command=self.txt_data.yview)
        self.txt_data.configure(yscrollcommand=sb.set)
        self.txt_data.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        # Botones
        btn_f = tk.Frame(body, bg=COLORS['bg_card'])
        btn_f.pack(fill='x', pady=(6, 2))
        btns = [
            ('Calcular', self._run, COLORS['primary'], COLORS['text_white']),
            ('Cargar estudio', self._load_demo, COLORS['secondary'], COLORS['text']),
            ('Limpiar', self._clear, '#CFD8DC', COLORS['text']),
        ]
        for txt, cmd, bg, fg in btns:
            tk.Button(btn_f, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Sección Excel
        tk.Frame(body, bg=COLORS['border'], height=1).pack(fill='x', pady=(4, 2))
        tk.Label(body, text='📋 Excel: columna A = valores de peso (lb)',
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['text_light']).pack(anchor='w')
        excel_row = tk.Frame(body, bg=COLORS['bg_card'])
        excel_row.pack(fill='x', pady=2)
        tk.Button(excel_row, text='📂 Cargar desde Excel', command=self._load_excel,
                  bg='#0277BD', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(
                      side='left', fill='x', expand=True, padx=(0, 3))
        tk.Button(excel_row, text='📄 Plantilla', command=self._gen_template,
                  bg='#37474F', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(side='left')

    def _toggle_sigma(self):
        if self.sigma_source.get() == 'manual':
            self.sigma_entry.configure(state='normal')
        else:
            self.sigma_entry.configure(state='disabled')

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
        tk.Label(hdr, text='Índices de Capacidad del Proceso', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)

        self.res_labels = {}

        # Fila 1: Estadísticos del proceso
        row1 = tk.Frame(body, bg=COLORS['bg_card'])
        row1.pack(fill='x', pady=2)
        proc_fields = [('μ (Media)', 'mu'), ('σ (Desv. Est.)', 'sigma'),
                       ('n (datos)', 'n')]
        for lbl, key in proc_fields:
            f = tk.Frame(row1, bg=COLORS['secondary_light'], bd=0,
                         highlightbackground=COLORS['secondary'], highlightthickness=1)
            f.pack(side='left', padx=6, pady=2, ipadx=8, ipady=4)
            tk.Label(f, text=lbl, font=FONTS['small'], bg=COLORS['secondary_light'],
                     fg=COLORS['text_light']).pack()
            lb = tk.Label(f, text='—', font=FONTS['result'],
                          bg=COLORS['secondary_light'], fg=COLORS['text'], width=12)
            lb.pack()
            self.res_labels[key] = lb

        # Fila 2: Índices principales
        row2 = tk.Frame(body, bg=COLORS['bg_card'])
        row2.pack(fill='x', pady=2)
        idx_fields = [('Cp', 'cp', COLORS['info']),
                      ('Cpk', 'cpk', COLORS['primary']),
                      ('Cpu', 'cpu', COLORS['warning']),
                      ('Cpl', 'cpl', COLORS['warning'])]
        for lbl, key, color in idx_fields:
            f = tk.Frame(row2, bg=color, bd=0)
            f.pack(side='left', padx=6, pady=2, ipadx=12, ipady=6)
            tk.Label(f, text=lbl, font=FONTS['subheader'],
                     bg=color, fg=COLORS['text_white']).pack()
            lb = tk.Label(f, text='—', font=('Segoe UI', 16, 'bold'),
                          bg=color, fg=COLORS['text_white'], width=8)
            lb.pack()
            self.res_labels[key] = lb

        # Evaluación
        self.eval_lbl = tk.Label(body, text='', font=FONTS['label_b'],
                                 bg=COLORS['bg_card'], fg=COLORS['text'])
        self.eval_lbl.pack(anchor='w', padx=4, pady=(2, 0))

        # Fila 3: % No conformes
        row3 = tk.Frame(body, bg=COLORS['bg_card'])
        row3.pack(fill='x', pady=2)
        pnc_fields = [('% PNC (LSE)', 'pnc_sup'), ('% PNC (LIE)', 'pnc_inf'),
                      ('% PNC Total', 'pnc_total')]
        for lbl, key in pnc_fields:
            f = tk.Frame(row3, bg='#FFEBEE', bd=0,
                         highlightbackground=COLORS['danger'], highlightthickness=1)
            f.pack(side='left', padx=6, pady=2, ipadx=8, ipady=4)
            tk.Label(f, text=lbl, font=FONTS['small'],
                     bg='#FFEBEE', fg=COLORS['danger']).pack()
            lb = tk.Label(f, text='—', font=FONTS['result'],
                          bg='#FFEBEE', fg=COLORS['danger'], width=12)
            lb.pack()
            self.res_labels[key] = lb

    def _build_charts(self, parent):
        self._cc_cap = CollapsibleChart(
            parent, 'Análisis de Capacidad del Proceso', figsize=(6, 3.5))
        self._cc_cap.pack(side='left', fill='both', expand=True, padx=(0, 2))
        self.ax_cap = self._cc_cap.ax

        self._cc_pnc = CollapsibleChart(
            parent, 'Distribución de No Conformes', figsize=(6, 3.5))
        self._cc_pnc.pack(side='left', fill='both', expand=True, padx=(2, 0))
        self.ax_pnc = self._cc_pnc.ax

        self._draw_empty()

    def _draw_all(self):
        self._cc_cap.fig.tight_layout(pad=1.5)
        self._cc_pnc.fig.tight_layout(pad=1.5)
        self._cc_cap.draw()
        self._cc_pnc.draw()

    def _draw_empty(self):
        for ax, title in [(self.ax_cap, 'Análisis de Capacidad del Proceso'),
                          (self.ax_pnc, 'Distribución de No Conformes')]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
        self._draw_all()

    # ── Lógica ───────────────────────────────────────────────────────────────
    def _get_data(self):
        raw = self.txt_data.get('1.0', 'end').strip()
        if not raw:
            return None
        tokens = raw.replace(',', ' ').replace('\n', ' ').replace(';', ' ').split()
        vals = [parse_value(t) for t in tokens if parse_value(t) is not None]
        return vals if len(vals) >= 5 else None

    def _run(self):
        data = self._get_data()
        if data is None:
            messagebox.showwarning('Datos insuficientes',
                                   'Ingrese al menos 5 valores de peso.')
            return
        try:
            lie = parse_value(self.spec_entries['lie'].get())
            lse = parse_value(self.spec_entries['lse'].get())
            if lie is None or lse is None or lie >= lse:
                messagebox.showerror('Especificaciones inválidas',
                                     'Ingrese LIE < LSE válidos.')
                return

            sigma = None
            if self.sigma_source.get() == 'manual':
                sigma = parse_value(self.sigma_entry.get())

            target = parse_value(self.spec_entries['target'].get())
            cap = compute_capability(data, lie, lse, sigma)
            s = summary_stats(data)

            self._update_results(cap, s)
            self._draw_charts(data, cap, lie, lse, target)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _update_results(self, cap, s):
        self.res_labels['mu'].configure(text=f"{cap['mu']:.5f} lb")
        self.res_labels['sigma'].configure(text=f"{cap['sigma']:.5f} lb")
        self.res_labels['n'].configure(text=str(s['n']))

        for key in ['cp', 'cpk', 'cpu', 'cpl']:
            val = cap[key]
            self.res_labels[key].configure(text=f"{val:.4f}")

        for key in ['pnc_sup', 'pnc_inf', 'pnc_total']:
            val = cap[key]
            self.res_labels[key].configure(text=f"{val*100:.2f}%")

        # Evaluación cualitativa
        cpk = cap['cpk']
        if cpk >= 1.67:
            msg   = '✔ Proceso excelente (Cpk ≥ 1.67)'
            color = COLORS['success']
        elif cpk >= 1.33:
            msg   = '✔ Proceso capaz (Cpk ≥ 1.33)'
            color = COLORS['success']
        elif cpk >= 1.00:
            msg   = '⚠ Proceso marginalmente capaz (1.00 ≤ Cpk < 1.33)'
            color = COLORS['warning']
        elif cpk >= 0.67:
            msg   = '✘ Proceso no capaz (0.67 ≤ Cpk < 1.00) – se requieren mejoras'
            color = COLORS['danger']
        else:
            msg   = '✘ Proceso muy incapaz (Cpk < 0.67) – acción urgente'
            color = COLORS['danger']
        self.eval_lbl.configure(text=msg, fg=color)

    def _draw_charts(self, data, cap, lie, lse, target):
        data = np.array(data)
        mu    = cap['mu']
        sigma = cap['sigma']

        # ── Gráfico de capacidad ──
        ax = self.ax_cap
        ax.clear()
        ax.set_facecolor('#FAFAFA')

        x_min = min(data.min(), lie) - 2*sigma
        x_max = max(data.max(), lse) + 2*sigma
        x = np.linspace(x_min, x_max, 500)
        y = stats.norm.pdf(x, mu, sigma)

        # Área fuera de especificación
        x_below = x[x < lie]
        x_above = x[x > lse]
        ax.fill_between(x_below, stats.norm.pdf(x_below, mu, sigma),
                        alpha=0.35, color=COLORS['danger'], label='No conforme (LIE)')
        ax.fill_between(x_above, stats.norm.pdf(x_above, mu, sigma),
                        alpha=0.35, color=COLORS['accent'], label='No conforme (LSE)')
        ax.fill_between(x[(x >= lie) & (x <= lse)],
                        stats.norm.pdf(x[(x >= lie) & (x <= lse)], mu, sigma),
                        alpha=0.25, color=COLORS['primary_lighter'], label='Conforme')

        ax.plot(x, y, color=COLORS['primary'], linewidth=2, label=f'Normal(μ={mu:.3f}, σ={sigma:.4f})')

        ax.axvline(lie, color=COLORS['chart_spec_l'], linewidth=1.8, linestyle='--', label=f'LIE={lie}')
        ax.axvline(lse, color=COLORS['chart_spec_u'], linewidth=1.8, linestyle='--', label=f'LSE={lse}')
        ax.axvline(mu,  color=COLORS['primary'],  linewidth=1.5, linestyle='-',  label=f'μ={mu:.3f}')
        if target:
            ax.axvline(target, color=COLORS['chart_target'], linewidth=1.2, linestyle='-.',
                       label=f'Objetivo={target}', alpha=0.8)

        ax.set_xlabel('Peso (lb)', fontsize=9)
        ax.set_ylabel('Densidad', fontsize=9)
        ax.set_title(f'Capacidad del Proceso  Cp={cap["cp"]:.3f}  Cpk={cap["cpk"]:.3f}',
                     fontsize=10, fontweight='bold')
        ax.legend(fontsize=6.5, loc='upper right')
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.25, linestyle=':')

        # ── Gráfico de PNC ──
        ax2 = self.ax_pnc
        ax2.clear()
        ax2.set_facecolor('#FAFAFA')

        categorias = ['Por encima\nde LSE', 'Por debajo\nde LIE', 'Total\nno conforme']
        valores_pct = [cap['pnc_sup']*100, cap['pnc_inf']*100, cap['pnc_total']*100]
        bar_colors  = [COLORS['accent'], COLORS['danger'], COLORS['primary_light']]
        bars = ax2.bar(categorias, valores_pct, color=bar_colors, edgecolor='white',
                       linewidth=0.8, width=0.5)
        for bar, val in zip(bars, valores_pct):
            ax2.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.3,
                     f'{val:.2f}%', ha='center', va='bottom',
                     fontsize=9, fontweight='bold', color=COLORS['text'])
        ax2.set_ylabel('% Productos No Conformes', fontsize=9)
        ax2.set_title('Distribución de No Conformes', fontsize=10, fontweight='bold')
        ax2.tick_params(labelsize=8)
        ax2.grid(True, alpha=0.25, linestyle=':', axis='y')
        ax2.set_ylim(0, max(valores_pct)*1.25 + 2)

        self._draw_all()

    def _load_excel(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_read_single_col
        fp = filedialog.askopenfilename(
            title='Seleccionar archivo Excel – Datos de peso',
            filetypes=[('Excel', '*.xlsx *.xls'), ('Todos', '*.*')])
        if not fp:
            return
        try:
            values = excel_read_single_col(fp)
            if not values:
                messagebox.showwarning('Sin datos',
                    'No se encontraron valores numéricos en la columna A.\n'
                    'Fila 1 = encabezado, filas 2+ = valores de peso.')
                return
            self.txt_data.delete('1.0', 'end')
            self.txt_data.insert('1.0', '\n'.join(str(v) for v in values))
            messagebox.showinfo('Excel cargado', f'{len(values)} valores cargados correctamente.')
        except Exception as e:
            messagebox.showerror('Error al leer Excel', str(e))

    def _gen_template(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_create_template
        fp = filedialog.asksaveasfilename(
            title='Guardar plantilla Excel',
            defaultextension='.xlsx',
            initialfile='Plantilla_Capacidad.xlsx',
            filetypes=[('Excel', '*.xlsx')])
        if not fp:
            return
        try:
            excel_create_template(fp, 'single_col')
            messagebox.showinfo('Plantilla creada',
                f'Plantilla guardada en:\n{fp}\n\n'
                'Formato: columna A = "Peso (lb)", filas 2+ = valores.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _load_demo(self):
        flat = [v for row in FASE_I_DATA for v in row]
        self.txt_data.delete('1.0', 'end')
        self.txt_data.insert('1.0', '\n'.join(str(v) for v in flat))
        # Usar sigma del estudio
        self.sigma_source.set('manual')
        self.sigma_entry.configure(state='normal')
        self.sigma_entry.delete(0, 'end')
        self.sigma_entry.insert(0, '0.09865')

    def _clear(self):
        self.txt_data.delete('1.0', 'end')
        for lb in self.res_labels.values():
            lb.configure(text='—', fg=COLORS['primary'])
        self.eval_lbl.configure(text='')
        self.sigma_source.set('datos')
        self.sigma_entry.configure(state='disabled')
        self._draw_empty()
