# -*- coding: utf-8 -*-
"""
Módulo: Análisis de Normalidad
Sistema SPC – PMD y Cía S.C.A.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS, FASE_I_DATA
from utils.spc_utils import (normality_tests, summary_stats, parse_value,
                              durbin_watson, runs_test, acf_lag1)
from utils.widgets import CollapsibleChart


class NormalidadModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._build_ui()

    # ── Layout principal ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Instrucción
        inst = tk.Label(self, text=(
            "Ingrese los datos individuales de peso (lb) — un valor por línea o separados por espacios/comas. "
            "Luego presione  Analizar."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=900, justify='left')
        inst.pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=6, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=6)

        # Panel izquierdo – entrada de datos
        left = tk.Frame(paned, bg=COLORS['bg_card'], bd=0,
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=260, width=290)
        self._build_left(left)

        # Panel derecho – gráficos y resultados
        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=500)
        self._build_right(right)

    def _build_left(self, parent):
        # Cabecera
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Datos de Entrada', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12)

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='both', expand=True, padx=10, pady=8)

        tk.Label(body, text='Valores de Peso (lb):', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).pack(anchor='w', pady=(4, 2))

        # Área de texto para datos
        txt_frame = tk.Frame(body, bg=COLORS['border'], bd=1)
        txt_frame.pack(fill='x', pady=4)
        self.txt_data = tk.Text(txt_frame, font=FONTS['entry'], width=22, height=13,
                                bd=0, padx=6, pady=6, wrap='none',
                                relief='flat', bg=COLORS['bg_card'])
        sb = ttk.Scrollbar(txt_frame, orient='vertical', command=self.txt_data.yview)
        self.txt_data.configure(yscrollcommand=sb.set)
        self.txt_data.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        # Nivel de significancia
        sigf = tk.Frame(body, bg=COLORS['bg_card'])
        sigf.pack(fill='x', pady=(8, 4))
        tk.Label(sigf, text='Nivel de significancia (α):', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text']).pack(side='left')
        self.alpha_var = tk.StringVar(value='0.05')
        alpha_cb = ttk.Combobox(sigf, textvariable=self.alpha_var, width=7, state='readonly',
                                values=['0.01', '0.05', '0.10'])
        alpha_cb.pack(side='left', padx=6)

        # Botones principales
        btn_frame = tk.Frame(body, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', pady=6)
        self._btn(btn_frame, 'Analizar', self._run_analysis,
                  COLORS['primary'], COLORS['text_white']).pack(fill='x', pady=2)
        self._btn(btn_frame, 'Cargar datos del estudio', self._load_demo,
                  COLORS['secondary'], COLORS['text']).pack(fill='x', pady=2)
        self._btn(btn_frame, 'Limpiar', self._clear,
                  COLORS['bg_dark'] if 'bg_dark' in COLORS else '#CFD8DC',
                  COLORS['text']).pack(fill='x', pady=2)

        # Sección Excel
        tk.Frame(body, bg=COLORS['border'], height=1).pack(fill='x', pady=(6, 2))
        tk.Label(body, text='📋 Excel: columna A = valores de peso (lb)',
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['text_light']).pack(anchor='w')
        excel_row = tk.Frame(body, bg=COLORS['bg_card'])
        excel_row.pack(fill='x', pady=2)
        self._btn(excel_row, '📂 Cargar desde Excel', self._load_excel,
                  '#0277BD', COLORS['text_white']).pack(side='left', fill='x', expand=True, padx=(0, 3))
        self._btn(excel_row, '📄 Plantilla', self._gen_template,
                  '#37474F', COLORS['text_white']).pack(side='left')

    def _build_right(self, parent):
        # Resultados numéricos
        res_frame = tk.Frame(parent, bg=COLORS['bg_card'],
                             highlightbackground=COLORS['border'], highlightthickness=1)
        res_frame.pack(fill='x', padx=6, pady=(0, 6))
        self._build_results_panel(res_frame)

        # Pruebas de independencia (panel colapsable)
        self._build_independence_section(parent)

        # Gráficos
        chart_frame = tk.Frame(parent, bg=COLORS['bg'])
        chart_frame.pack(fill='both', expand=True, padx=6)
        self._build_charts(chart_frame)

    def _build_results_panel(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Resultados de Pruebas de Normalidad', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)

        # Estadísticas descriptivas
        stats_frame = tk.LabelFrame(body, text='Estadísticas Descriptivas',
                                    bg=COLORS['bg_card'], fg=COLORS['text'],
                                    font=FONTS['label_b'])
        stats_frame.pack(fill='x', pady=(0, 8))

        self.stats_labels = {}
        fields = [('n', 'n'), ('mean', 'Media (μ)'), ('std', 'Desv. Est. (σ)'),
                  ('median', 'Mediana'), ('min', 'Mínimo'), ('max', 'Máximo')]
        for i, (key, label) in enumerate(fields):
            r, c = divmod(i, 3)
            tk.Label(stats_frame, text=label + ':', font=FONTS['label_b'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                         row=r, column=c*2, sticky='e', padx=(12, 2), pady=3)
            lbl = tk.Label(stats_frame, text='—', font=FONTS['label'],
                           bg=COLORS['bg_card'], fg=COLORS['text'], width=10, anchor='w')
            lbl.grid(row=r, column=c*2+1, sticky='w', pady=3)
            self.stats_labels[key] = lbl

        # Tabla de pruebas
        tests_frame = tk.LabelFrame(body, text='Pruebas de Hipótesis (H₀: Los datos siguen distribución normal)',
                                    bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['label_b'])
        tests_frame.pack(fill='x')

        cols = ['Prueba', 'Estadístico', 'Valor-p', 'α', 'Conclusión']
        for j, col in enumerate(cols):
            tk.Label(tests_frame, text=col, font=FONTS['label_b'],
                     bg=COLORS['primary'], fg=COLORS['text_white'],
                     padx=8, pady=4, relief='flat').grid(row=0, column=j, sticky='ew', padx=1)
        tests_frame.columnconfigure(list(range(len(cols))), weight=1)

        self.test_rows = {}
        test_names = [('AD', 'Anderson-Darling'), ('SW', 'Shapiro-Wilk'), ('KS', 'Kolmogorov-Smirnov')]
        for i, (key, name) in enumerate(test_names):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            cells = []
            vals = [name, '—', '—', '—', '—']
            for j, val in enumerate(vals):
                lbl = tk.Label(tests_frame, text=val, font=FONTS['label'],
                               bg=bg, fg=COLORS['text'], padx=6, pady=4, anchor='center')
                lbl.grid(row=i+1, column=j, sticky='ew', padx=1, pady=1)
                cells.append(lbl)
            self.test_rows[key] = cells

    def _build_charts(self, parent):
        self._cc_hist = CollapsibleChart(
            parent, 'Histograma con curva normal', figsize=(6, 3.5))
        self._cc_hist.pack(side='left', fill='both', expand=True, padx=(0, 2))
        self.ax_hist = self._cc_hist.ax

        self._cc_qq = CollapsibleChart(
            parent, 'Gráfico de Probabilidad Normal (Q-Q)', figsize=(6, 3.5))
        self._cc_qq.pack(side='left', fill='both', expand=True, padx=(2, 0))
        self.ax_qq = self._cc_qq.ax

        self._draw_empty_charts()

    def _draw_all(self):
        self._cc_hist.fig.tight_layout(pad=1.5)
        self._cc_qq.fig.tight_layout(pad=1.5)
        self._cc_hist.draw()
        self._cc_qq.draw()

    def _draw_empty_charts(self):
        for ax, title in [(self.ax_hist, 'Histograma con curva normal'),
                          (self.ax_qq,   'Gráfico de Probabilidad Normal (Q-Q)')]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
            ax.tick_params(labelsize=8)
        self._draw_all()

    # ── Lógica ───────────────────────────────────────────────────────────────
    def _get_data(self):
        raw = self.txt_data.get('1.0', 'end').strip()
        if not raw:
            return None
        tokens = raw.replace(',', ' ').replace('\n', ' ').replace(';', ' ').split()
        vals = []
        for t in tokens:
            v = parse_value(t)
            if v is not None:
                vals.append(v)
        return vals if len(vals) >= 3 else None

    def _run_analysis(self):
        data = self._get_data()
        if data is None:
            messagebox.showwarning('Datos insuficientes',
                                   'Ingrese al menos 3 valores numéricos de peso.')
            return
        try:
            alpha = float(self.alpha_var.get())
            self._update_stats(data)
            results = normality_tests(data)
            self._update_test_table(results, alpha)
            self._update_charts(data)
            self._run_independence_tests(data, alpha)
        except Exception as e:
            messagebox.showerror('Error de cálculo', str(e))

    def _update_stats(self, data):
        s = summary_stats(data)
        fmt = {
            'n':      f"{s['n']}",
            'mean':   f"{s['mean']:.4f} lb",
            'std':    f"{s['std']:.5f} lb",
            'median': f"{s['median']:.4f} lb",
            'min':    f"{s['min']:.4f} lb",
            'max':    f"{s['max']:.4f} lb",
        }
        for key, lbl in self.stats_labels.items():
            lbl.configure(text=fmt.get(key, '—'))

    def _update_test_table(self, results, alpha):
        test_map = {
            'AD': ('Anderson-Darling', results['AD']),
            'SW': ('Shapiro-Wilk',     results['SW']),
            'KS': ('Kolmogorov-Smirnov', results['KS']),
        }
        for i, (key, (name, res)) in enumerate(test_map.items()):
            cells = self.test_rows[key]
            stat = f"{res['statistic']:.4f}"
            pval = f"{res['p_value']:.4f}"
            alph = f"{alpha:.2f}"
            if res['normal']:
                conclusion = '✔ Normal (No se rechaza H₀)'
                color = COLORS['success']
            else:
                conclusion = '✘ No normal (Se rechaza H₀)'
                color = COLORS['danger']
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            for j, val in enumerate([name, stat, pval, alph, conclusion]):
                cells[j].configure(text=val, bg=bg,
                                   fg=color if j == 4 else COLORS['text'],
                                   font=(FONTS['label_b'] if j == 4 else FONTS['label']))

    def _update_charts(self, data):
        data = np.array(data)
        mu   = data.mean()
        sigma = data.std(ddof=1)

        # ── Histograma ──
        ax = self.ax_hist
        ax.clear()
        ax.set_facecolor('#FAFAFA')
        n_bins = max(8, int(np.sqrt(len(data))))
        ax.hist(data, bins=n_bins, density=True, color=COLORS['primary_lighter'],
                edgecolor='white', alpha=0.8, linewidth=0.5, label='Datos')
        x = np.linspace(data.min() - sigma, data.max() + sigma, 300)
        from scipy.stats import norm
        ax.plot(x, norm.pdf(x, mu, sigma), color=COLORS['danger'],
                linewidth=2, label=f'Normal(μ={mu:.3f}, σ={sigma:.4f})')
        ax.axvline(mu, color=COLORS['chart_cl'], linewidth=1.5, linestyle='--', label='Media')
        ax.set_xlabel('Peso (lb)', fontsize=9)
        ax.set_ylabel('Densidad', fontsize=9)
        ax.set_title('Histograma con curva normal', fontsize=10, fontweight='bold')
        ax.legend(fontsize=7)
        ax.tick_params(labelsize=8)

        # ── Q-Q Plot ──
        ax2 = self.ax_qq
        ax2.clear()
        ax2.set_facecolor('#FAFAFA')
        from scipy.stats import probplot
        (osm, osr), (slope, intercept, r) = probplot(data, dist='norm')
        ax2.scatter(osm, osr, color=COLORS['chart_data'], s=20, zorder=3, label='Datos')
        fit_line = np.array(osm) * slope + intercept
        ax2.plot(osm, fit_line, color=COLORS['danger'], linewidth=1.5,
                 label=f'Línea de referencia (R²={r**2:.4f})')
        ax2.set_xlabel('Cuantiles teóricos', fontsize=9)
        ax2.set_ylabel('Cuantiles observados', fontsize=9)
        ax2.set_title('Gráfico de Probabilidad Normal (Q-Q)', fontsize=10, fontweight='bold')
        ax2.legend(fontsize=7)
        ax2.tick_params(labelsize=8)

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
                    'Asegúrese de que la fila 1 sea el encabezado y los datos estén en la columna A.')
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
            initialfile='Plantilla_Normalidad.xlsx',
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
        lines = [str(v) for v in flat]
        self.txt_data.insert('1.0', '\n'.join(lines))

    def _clear(self):
        self.txt_data.delete('1.0', 'end')
        for lbl in self.stats_labels.values():
            lbl.configure(text='—')
        for cells in self.test_rows.values():
            for j, cell in enumerate(cells):
                if j != 0:
                    cell.configure(text='—', fg=COLORS['text'],
                                   font=FONTS['label'])
        self._reset_independence_table()
        self._draw_empty_charts()

    # ── Pruebas de independencia ──────────────────────────────────────────────

    def _build_independence_section(self, parent):
        """Construye el panel colapsable de pruebas de independencia/aleatoriedad."""
        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill='x', padx=6, pady=(0, 4))

        hdr = tk.Frame(outer, bg='#37474F', cursor='hand2')
        hdr.pack(fill='x')
        self._ind_arrow = tk.Label(hdr, text='▶', font=FONTS['label_b'],
                                   bg='#37474F', fg=COLORS['text_white'],
                                   cursor='hand2', padx=10, pady=5)
        self._ind_arrow.pack(side='right')
        title_lbl = tk.Label(hdr,
            text='Pruebas de Independencia y Aleatoriedad (supuesto SPC)',
            font=FONTS['label_b'], bg='#37474F',
            fg=COLORS['text_white'], padx=10, pady=5, anchor='w')
        title_lbl.pack(side='left', fill='x', expand=True)
        for w in (hdr, self._ind_arrow, title_lbl):
            w.bind('<Button-1>', self._toggle_independence)

        self._ind_body = tk.Frame(outer, bg=COLORS['bg_card'],
                                  highlightbackground=COLORS['border'],
                                  highlightthickness=1)
        self._ind_expanded = False

        # Subtítulo explicativo
        tk.Label(self._ind_body,
            text=('H₀: Las observaciones son independientes y aleatorias. '
                  'Violación indica autocorrelación o patrones sistemáticos.'),
            bg=COLORS['bg_card'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=700, justify='left').pack(fill='x', padx=10, pady=(6, 2))

        # Tabla de resultados
        tbl = tk.Frame(self._ind_body, bg=COLORS['bg_card'])
        tbl.pack(fill='x', padx=10, pady=(2, 8))
        cols = ['Prueba', 'Estadístico', 'Detalle', 'α', 'Conclusión']
        widths = [22, 14, 26, 6, 32]
        for j, (col, w) in enumerate(zip(cols, widths)):
            tk.Label(tbl, text=col, font=FONTS['label_b'],
                     bg=COLORS['primary'], fg=COLORS['text_white'],
                     width=w, pady=4).grid(row=0, column=j, padx=1, pady=1, sticky='ew')

        self._ind_rows = {}
        test_defs = [
            ('DW',   'Durbin-Watson'),
            ('RUNS', 'Prueba de rachas'),
            ('ACF',  'Autocorrelación lag-1'),
        ]
        for i, (key, name) in enumerate(test_defs):
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            cells = []
            for j, (w, val) in enumerate(zip(widths, [name, '—', '—', '—', '—'])):
                lbl = tk.Label(tbl, text=val, font=FONTS['label'],
                               bg=bg, fg=COLORS['text'], width=w,
                               pady=4, anchor='center')
                lbl.grid(row=i+1, column=j, padx=1, pady=1, sticky='ew')
                cells.append(lbl)
            self._ind_rows[key] = cells

    def _toggle_independence(self, event=None):
        if self._ind_expanded:
            self._ind_body.pack_forget()
            self._ind_arrow.configure(text='▶')
        else:
            self._ind_body.pack(fill='x')
            self._ind_arrow.configure(text='▼')
        self._ind_expanded = not self._ind_expanded

    def _run_independence_tests(self, data, alpha=0.05):
        """Calcula y muestra las tres pruebas de independencia."""
        dw   = durbin_watson(data)
        rt   = runs_test(data)
        acf  = acf_lag1(data)

        alpha_str = f'{alpha:.2f}'
        rows_data = [
            ('DW', [
                f"DW = {dw['statistic']:.4f}",
                dw['interpretation'],
                alpha_str,
                ('✔ Independientes' if dw['independent']
                 else '✘ Autocorrelación detectada'),
                dw['independent'],
            ]),
            ('RUNS', [
                f"Z = {rt['z']:.4f}",
                f"Rachas={rt['runs']}  n+={rt['n_above']}  n−={rt['n_below']}  p={rt['p_value']:.4f}",
                alpha_str,
                ('✔ Aleatoriedad confirmada' if rt['independent']
                 else '✘ Patrón no aleatorio detectado'),
                rt['independent'],
            ]),
            ('ACF', [
                f"r₁ = {acf['r1']:.4f}",
                f"Z = {acf['z']:.4f}  p = {acf['p_value']:.4f}",
                alpha_str,
                ('✔ Sin autocorrelación significativa' if acf['independent']
                 else '✘ Autocorrelación lag-1 significativa'),
                acf['independent'],
            ]),
        ]
        for i, (key, row_vals) in enumerate(rows_data):
            cells = self._ind_rows[key]
            stat_txt, detail_txt, alp_txt, concl_txt, ok = row_vals
            bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_row_alt']
            color = COLORS['success'] if ok else COLORS['danger']
            # col 0 = nombre (unchanged), col 1..4
            cells[1].configure(text=stat_txt,  fg=COLORS['text'],   bg=bg, font=FONTS['label'])
            cells[2].configure(text=detail_txt, fg=COLORS['text'],   bg=bg, font=FONTS['label'])
            cells[3].configure(text=alp_txt,    fg=COLORS['text'],   bg=bg, font=FONTS['label'])
            cells[4].configure(text=concl_txt,  fg=color,            bg=bg, font=FONTS['label_b'])

        # Auto-expand la sección si hay alguna violación
        any_fail = not (dw['independent'] and rt['independent'] and acf['independent'])
        if any_fail and not self._ind_expanded:
            self._toggle_independence()

    def _reset_independence_table(self):
        for cells in self._ind_rows.values():
            for j in range(1, 5):
                cells[j].configure(text='—', fg=COLORS['text'], font=FONTS['label'])

    @staticmethod
    def _btn(parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                         font=FONTS['label_b'], relief='flat', bd=0,
                         activebackground=COLORS['primary_lighter'],
                         activeforeground=COLORS['text_white'],
                         cursor='hand2', padx=10, pady=6)
