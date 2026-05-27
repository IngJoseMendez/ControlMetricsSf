# -*- coding: utf-8 -*-
"""
Módulo: Herramienta de Diseño ARL / ATS  (Módulo 6)
ControlMetrics – PMD y Cía S.C.A.

Permite calcular y comparar el desempeño estadístico de cartas de control
X-barra / I-MR en términos de:
  • ARL₀  – Longitud de corrida en control  (objetivo ≈ 370.4 para k=3)
  • ARL₁  – Longitud de corrida fuera de control
  • ATS₀  – Tiempo promedio de señal en control  (ARL₀ × h)
  • ATS₁  – Tiempo promedio de señal fuera de control (ARL₁ × h)
  • Curva OC – Probabilidad de NO detectar el corrimiento
  • Curva ARL – ARL₁ vs corrimiento δ (en unidades de σ)

Hasta 3 diseños pueden compararse simultáneamente.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS
from utils.spc_utils import parse_value
from utils.widgets import CollapsibleChart


# ── Paleta de colores para las 3 curvas ──────────────────────────────────────
_CURVE_COLORS = ['#1565C0', '#C62828', '#2E7D32']
_CURVE_STYLES = ['-',       '--',      '-.']


def _arl_curve(k, n, delta_range):
    """
    Calcula ARL y beta para carta X-barra dado k (factor LCS/LCI en σ̂/√n),
    n (tamaño de subgrupo) y un vector de corrimientos δ en unidades de σ.

    Para I-MR use n=1.
    ARL₀ se obtiene con δ=0 → ARL ≈ 370.4 si k=3.
    """
    d = np.asarray(delta_range, dtype=float)
    beta = (stats.norm.cdf( k - d * np.sqrt(n)) -
            stats.norm.cdf(-k - d * np.sqrt(n)))
    beta = np.clip(beta, 0.0, 1.0)
    power = 1.0 - beta
    arl = np.where(power > 0, 1.0 / power, np.inf)
    return beta, arl


class CartasDisenoModule(tk.Frame):
    """Herramienta de diseño ARL / ATS para cartas X̄ e I-MR."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._results_cache = []   # lista de dicts por diseño
        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self,
            text=("Diseñe y compare cartas de control X̄ / I-MR evaluando ARL₀, ARL₁ y "
                  "ATS para distintos parámetros (n, k, h). "
                  "Un ARL₀ ≈ 370.4 corresponde a k = 3σ (riesgo α ≈ 0.27 %)."),
            bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=1000, justify='left').pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=6, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=310, width=340)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=560)
        self._build_right(right)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL IZQUIERDO  (parámetros de entrada)
    # ─────────────────────────────────────────────────────────────────────────
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
        p = inner   # alias

        # ── Cabecera ──────────────────────────────────────────────────────────
        hdr = tk.Frame(p, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Herramienta de Diseño ARL / ATS',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, anchor='w')

        # ── Rango de corrimientos δ ────────────────────────────────────────────
        lf0 = tk.LabelFrame(p, text='Rango de corrimientos δ (en unidades de σ)',
                            bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        lf0.pack(fill='x', padx=10, pady=(8, 4))
        g0 = tk.Frame(lf0, bg=COLORS['bg_card'])
        g0.pack(fill='x', padx=6, pady=4)
        self.d_entries = {}
        for col, (lbl, key, val) in enumerate([
                ('δ mín:', 'dmin', '0.0'),
                ('δ máx:', 'dmax', '4.0'),
                ('Paso:',  'step', '0.1')]):
            tk.Label(g0, text=lbl, font=FONTS['small'], bg=COLORS['bg_card'],
                     fg=COLORS['text_light']).grid(row=0, column=col*2, sticky='e', padx=(4, 2))
            e = tk.Entry(g0, width=7, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, val)
            e.grid(row=0, column=col*2+1, sticky='w', padx=(0, 6))
            self.d_entries[key] = e

        # ── Diseños (hasta 3) ──────────────────────────────────────────────────
        self.design_frames = []   # lista de dicts con entries
        design_defaults = [
            {'label': 'Diseño 1 (principal)',  'n': '6',  'k': '3.0', 'h': '0.25', 'color': '#E3F2FD'},
            {'label': 'Diseño 2 (comparación)','n': '5',  'k': '3.0', 'h': '0.25', 'color': '#FCE4EC'},
            {'label': 'Diseño 3 (comparación)','n': '4',  'k': '2.75','h': '0.25', 'color': '#F1F8E9'},
        ]
        for i, dd in enumerate(design_defaults):
            lfi = tk.LabelFrame(p, text=dd['label'],
                                bg=dd['color'], fg=COLORS['text'], font=FONTS['small'])
            lfi.pack(fill='x', padx=10, pady=(4, 2))
            gi = tk.Frame(lfi, bg=dd['color'])
            gi.pack(fill='x', padx=6, pady=4)

            # Checkbox activo
            active_var = tk.BooleanVar(value=(i == 0))
            entries = {'active': active_var, 'color': _CURVE_COLORS[i]}

            # Activar/desactivar row
            chk = tk.Checkbutton(gi, text='Activo', variable=active_var,
                                 bg=dd['color'], fg=COLORS['text'],
                                 font=FONTS['small'], activebackground=dd['color'])
            chk.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 2))

            for row, (lbl2, key2, val2, tip) in enumerate([
                    ('n (subgr.):', 'n', dd['n'],
                     '1 = I-MR, 2-10 = X̄-R/S'),
                    ('k (factor):',  'k', dd['k'],
                     'Nro. de σ para LCS/LCI (usual: 3.0)'),
                    ('h (intervalo, h):', 'h', dd['h'],
                     'Intervalo de muestreo en horas')], start=1):
                tk.Label(gi, text=lbl2, font=FONTS['small'], bg=dd['color'],
                         fg=COLORS['text_light']).grid(row=row, column=0, sticky='e', padx=(2, 4), pady=2)
                e = tk.Entry(gi, width=9, font=FONTS['entry'], bd=1, relief='solid',
                             bg=COLORS['bg_card'])
                e.insert(0, val2)
                e.grid(row=row, column=1, sticky='w', padx=(0, 4), pady=2)
                # Tooltip text (small label)
                tk.Label(gi, text=tip, font=('Segoe UI', 7), bg=dd['color'],
                         fg=COLORS['text_light']).grid(row=row, column=2, sticky='w', padx=2)
                entries[key2] = e

            self.design_frames.append(entries)

        # ── Botón calcular ─────────────────────────────────────────────────────
        bf = tk.Frame(p, bg=COLORS['bg_card'])
        bf.pack(fill='x', padx=10, pady=(8, 4))
        tk.Button(bf, text='▶  Calcular ARL / ATS',
                  command=self._run,
                  bg=COLORS['primary'], fg=COLORS['text_white'],
                  font=FONTS['label_b'], relief='flat', bd=0,
                  cursor='hand2', padx=12, pady=7).pack(fill='x')

        # ── Resumen ARL₀ (resultados rápidos) ─────────────────────────────────
        sf = tk.LabelFrame(p, text='Resumen ARL₀ / ATS₀ (en control)',
                           bg=COLORS['secondary_light'], fg=COLORS['text'], font=FONTS['small'])
        sf.pack(fill='x', padx=10, pady=(4, 8))
        self._summary_inner = tk.Frame(sf, bg=COLORS['secondary_light'])
        self._summary_inner.pack(fill='x', padx=6, pady=4)
        self._summary_labels = []
        for i in range(3):
            lbl = tk.Label(self._summary_inner, text='', font=FONTS['small'],
                           bg=COLORS['secondary_light'], fg=COLORS['text'],
                           wraplength=280, justify='left', anchor='w')
            lbl.pack(fill='x', pady=1)
            self._summary_labels.append(lbl)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL DERECHO  (tabla + gráficas)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_right(self, parent):
        # Tabla de resultados
        tbl_frame = tk.Frame(parent, bg=COLORS['bg_card'],
                             highlightbackground=COLORS['border'], highlightthickness=1)
        tbl_frame.pack(fill='x', padx=6, pady=(0, 4))
        self._build_table_panel(tbl_frame)

        # Gráficas
        cf = tk.Frame(parent, bg=COLORS['bg'])
        cf.pack(fill='both', expand=True, padx=6, pady=4)

        self._cc_arl = CollapsibleChart(cf, 'Curva ARL  –  Longitud de corrida promedio vs corrimiento δ',
                                        figsize=(9, 2.9))
        self._cc_arl.pack(fill='both', expand=True, pady=(0, 2))

        self._cc_oc = CollapsibleChart(cf, 'Curva OC  –  Probabilidad de NO detectar el corrimiento',
                                       figsize=(9, 2.9))
        self._cc_oc.pack(fill='both', expand=True, pady=(2, 0))

        self._draw_empty()

    def _build_table_panel(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['bg_subheader'], pady=4)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Tabla de Resultados por Diseño',
                 font=FONTS['label_b'], bg=COLORS['bg_subheader'],
                 fg=COLORS['text_white']).pack(padx=10, anchor='w')

        tbl_outer = tk.Frame(parent, bg=COLORS['bg_card'])
        tbl_outer.pack(fill='x', padx=6, pady=4)

        # Canvas with horizontal scrollbar
        self._tbl_canvas = tk.Canvas(tbl_outer, bg=COLORS['bg_card'],
                                     height=140, highlightthickness=0)
        vsb = ttk.Scrollbar(tbl_outer, orient='vertical',
                            command=self._tbl_canvas.yview)
        hsb = ttk.Scrollbar(tbl_outer, orient='horizontal',
                            command=self._tbl_canvas.xview)
        self._tbl_canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self._tbl_canvas.pack(side='left', fill='both', expand=True)

        self._tbl_inner = tk.Frame(self._tbl_canvas, bg=COLORS['bg_card'])
        self._tbl_canvas.create_window((0, 0), window=self._tbl_inner, anchor='nw')
        self._tbl_inner.bind('<Configure>', lambda e: self._tbl_canvas.configure(
            scrollregion=self._tbl_canvas.bbox('all')))
        self._tbl_canvas.bind('<MouseWheel>', lambda e: self._tbl_canvas.yview_scroll(
            int(-1*(e.delta/120)), 'units'))

        self._build_table_headers()

    def _build_table_headers(self):
        for w in self._tbl_inner.winfo_children():
            w.destroy()
        cols = ['Diseño', 'n', 'k', 'h (h)', 'ARL₀', 'ATS₀ (h)',
                'ARL₁ (δ=1σ)', 'ATS₁ (δ=1σ)',
                'ARL₁ (δ=1.5σ)', 'ATS₁ (δ=1.5σ)',
                'ARL₁ (δ=2σ)', 'ATS₁ (δ=2σ)',
                'Potencia δ=1σ', 'α estimado']
        widths = [14, 5, 6, 7, 9, 10, 12, 13, 14, 15, 12, 13, 14, 11]
        bg_hdr = COLORS['primary']
        for j, (col, w) in enumerate(zip(cols, widths)):
            tk.Label(self._tbl_inner, text=col, font=FONTS['label_b'], bg=bg_hdr,
                     fg=COLORS['text_white'], width=w, pady=4,
                     relief='flat', bd=0).grid(row=0, column=j, padx=1, pady=1, sticky='ew')
        self._tbl_data_rows = []

    def _populate_table(self, results):
        """Agrega filas de datos a la tabla."""
        # Limpiar filas anteriores (dejar encabezado fila 0)
        for row_widgets in self._tbl_data_rows:
            for w in row_widgets:
                w.destroy()
        self._tbl_data_rows.clear()

        for ri, res in enumerate(results):
            bg = COLORS['bg_card'] if ri % 2 == 0 else COLORS['bg_row_alt']
            row_widgets = []
            vals = [
                res['label'],
                str(res['n']),
                f"{res['k']:.2f}",
                f"{res['h']:.3f}",
                f"{res['arl0']:.1f}",
                f"{res['ats0']:.2f}",
                f"{res['arl1_1s']:.2f}",
                f"{res['ats1_1s']:.2f}",
                f"{res['arl1_15s']:.2f}",
                f"{res['ats1_15s']:.2f}",
                f"{res['arl1_2s']:.2f}",
                f"{res['ats1_2s']:.2f}",
                f"{res['power_1s']*100:.1f} %",
                f"{res['alpha_est']*100:.3f} %",
            ]
            widths = [14, 5, 6, 7, 9, 10, 12, 13, 14, 15, 12, 13, 14, 11]
            for j, (val, wid) in enumerate(zip(vals, widths)):
                lbl = tk.Label(self._tbl_inner, text=val, font=FONTS['small'],
                               bg=bg, fg=COLORS['text'], width=wid,
                               relief='flat', bd=0, pady=3)
                lbl.grid(row=ri+1, column=j, padx=1, pady=1, sticky='ew')
                row_widgets.append(lbl)
            self._tbl_data_rows.append(row_widgets)

    # ─────────────────────────────────────────────────────────────────────────
    # CÁLCULO PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────
    def _run(self):
        # Leer rango δ
        try:
            dmin = float(self.d_entries['dmin'].get().replace(',', '.'))
            dmax = float(self.d_entries['dmax'].get().replace(',', '.'))
            step = float(self.d_entries['step'].get().replace(',', '.'))
            if step <= 0 or dmax <= dmin:
                raise ValueError
            delta_range = np.arange(dmin, dmax + step*0.001, step)
        except ValueError:
            messagebox.showwarning('Parámetros inválidos',
                'Verifique el rango δ (mín < máx, paso > 0).')
            return

        # Calcular cada diseño activo
        results = []
        for i, df in enumerate(self.design_frames):
            if not df['active'].get():
                continue
            try:
                n = int(df['n'].get().strip())
                k = float(df['k'].get().replace(',', '.'))
                h = float(df['h'].get().replace(',', '.'))
                if n < 1 or k <= 0 or h <= 0:
                    raise ValueError
            except (ValueError, KeyError):
                messagebox.showwarning('Datos inválidos',
                    f'Diseño {i+1}: verifique n, k y h.')
                return

            label = f'D{i+1}  n={n}  k={k:.2f}'
            beta_arr, arl_arr = _arl_curve(k, n, delta_range)

            # Puntos de referencia específicos
            def _point(delta_s):
                b_, a_ = _arl_curve(k, n, [delta_s])
                return float(b_[0]), float(a_[0])

            beta0, arl0 = _point(0.0)
            _,     arl1_1s  = _point(1.0)
            _,     arl1_15s = _point(1.5)
            _,     arl1_2s  = _point(2.0)
            beta1s, _ = _point(1.0)
            power_1s  = 1.0 - beta1s
            # α estimado (falsos positivos cuando el proceso está en control)
            alpha_est = 1.0 - beta0  if beta0 < 1.0 else 0.0

            results.append({
                'label':      label,
                'n': n, 'k': k, 'h': h,
                'color':      df['color'],
                'delta_arr':  delta_range,
                'beta_arr':   beta_arr,
                'arl_arr':    arl_arr,
                'arl0':       arl0,
                'ats0':       arl0 * h,
                'arl1_1s':    arl1_1s,
                'ats1_1s':    arl1_1s * h,
                'arl1_15s':   arl1_15s,
                'ats1_15s':   arl1_15s * h,
                'arl1_2s':    arl1_2s,
                'ats1_2s':    arl1_2s * h,
                'power_1s':   power_1s,
                'alpha_est':  alpha_est,
            })

        if not results:
            messagebox.showinfo('Sin diseños activos',
                'Active al menos un diseño antes de calcular.')
            return

        self._results_cache = results
        self._populate_table(results)
        self._update_summary(results)
        self._draw_charts(results)

    def _update_summary(self, results):
        for i, lbl in enumerate(self._summary_labels):
            if i < len(results):
                r = results[i]
                txt = (f"  {r['label']}:  "
                       f"ARL₀ = {r['arl0']:.1f}  |  ATS₀ = {r['ats0']:.2f} h  |  "
                       f"ARL₁(1σ) = {r['arl1_1s']:.2f}  |  "
                       f"Potencia(1σ) = {r['power_1s']*100:.1f}%")
                fg = r['color']
                lbl.configure(text=txt, fg=fg)
            else:
                lbl.configure(text='')

    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICAS
    # ─────────────────────────────────────────────────────────────────────────
    def _draw_empty(self):
        for cc, title, ylabel in [
                (self._cc_arl,
                 'Curva ARL  –  Longitud de corrida promedio vs δ',
                 'ARL₁  (subgrupos hasta señal)'),
                (self._cc_oc,
                 'Curva OC  –  Probabilidad de NO detectar el corrimiento',
                 'β  (P. de no detección)')]:
            ax = cc.ax
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=9, fontweight='bold', color=COLORS['text'])
            ax.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.text(0.5, 0.5, 'Sin datos – Configure parámetros y calcule',
                    ha='center', va='center', transform=ax.transAxes,
                    color=COLORS['text_light'], fontsize=9)
            ax.tick_params(labelsize=8)
            cc.fig.tight_layout(pad=1.5)
            cc.draw()

    def _draw_charts(self, results):
        # ── Curva ARL ──────────────────────────────────────────────────────────
        ax_arl = self._cc_arl.ax
        ax_arl.clear()
        ax_arl.set_facecolor('#FAFAFA')

        # Línea de referencia ARL₀ = 370.4 (k=3)
        ax_arl.axhline(370.4, color='#9E9E9E', lw=0.8, ls=':', alpha=0.6,
                       label='ARL₀=370.4 (k=3, referencia)')

        for r, ls in zip(results, _CURVE_STYLES):
            d_arr  = r['delta_arr']
            arl_arr = np.clip(r['arl_arr'], 1, 600)
            ax_arl.plot(d_arr, arl_arr, color=r['color'], lw=2, ls=ls,
                        label=r['label'])
            # Marcar punto δ=1σ
            idx1 = np.argmin(np.abs(d_arr - 1.0))
            ax_arl.plot(d_arr[idx1], arl_arr[idx1], 'o', color=r['color'],
                        ms=6, zorder=5)
            ax_arl.annotate(f"  {arl_arr[idx1]:.1f}",
                            (d_arr[idx1], arl_arr[idx1]),
                            fontsize=7, color=r['color'])

        ax_arl.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
        ax_arl.set_ylabel('ARL₁  (subgrupos hasta señal)', fontsize=8)
        ax_arl.set_title('Curva ARL  –  ARL₁ vs corrimiento δ',
                          fontsize=9, fontweight='bold', color=COLORS['text'])
        ax_arl.legend(fontsize=7, loc='upper right')
        ax_arl.tick_params(labelsize=8)
        ax_arl.grid(True, alpha=0.3, ls=':')
        ax_arl.set_ylim(bottom=0)
        self._cc_arl.fig.tight_layout(pad=1.5)
        self._cc_arl.draw()

        # ── Curva OC ───────────────────────────────────────────────────────────
        ax_oc = self._cc_oc.ax
        ax_oc.clear()
        ax_oc.set_facecolor('#FAFAFA')

        for r, ls in zip(results, _CURVE_STYLES):
            ax_oc.plot(r['delta_arr'], r['beta_arr'],
                       color=r['color'], lw=2, ls=ls, label=r['label'])
            # Marcar β en δ=1σ
            idx1 = np.argmin(np.abs(r['delta_arr'] - 1.0))
            b1   = r['beta_arr'][idx1]
            ax_oc.plot(r['delta_arr'][idx1], b1, 'o', color=r['color'], ms=6, zorder=5)
            ax_oc.annotate(f"  β={b1:.2f}",
                           (r['delta_arr'][idx1], b1),
                           fontsize=7, color=r['color'])

        # Líneas de referencia β
        ax_oc.axhline(0.5, color='#9E9E9E', lw=0.8, ls=':', alpha=0.5, label='β=0.50')
        ax_oc.axhline(0.1, color='#9E9E9E', lw=0.8, ls='--', alpha=0.5, label='β=0.10')

        ax_oc.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
        ax_oc.set_ylabel('β  (Probabilidad de no detección)', fontsize=8)
        ax_oc.set_title('Curva OC  –  Probabilidad de NO detectar el corrimiento',
                         fontsize=9, fontweight='bold', color=COLORS['text'])
        ax_oc.set_ylim(-0.02, 1.05)
        ax_oc.legend(fontsize=7, loc='upper right')
        ax_oc.tick_params(labelsize=8)
        ax_oc.grid(True, alpha=0.3, ls=':')
        self._cc_oc.fig.tight_layout(pad=1.5)
        self._cc_oc.draw()
