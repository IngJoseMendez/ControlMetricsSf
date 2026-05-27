# -*- coding: utf-8 -*-
"""
Módulo: Plan de Mejora – Sensibilidad del Sistema de Control
ControlMetrics – PMD y Cía S.C.A.

Permite:
  1. Evaluar la potencia actual de la carta X̄ para detectar un corrimiento
     específico de la media (Power = 1-β, NRL, ATS).
  2. Calcular el tamaño de muestra n necesario para alcanzar una potencia
     objetivo ante ese corrimiento.
  3. Visualizar la curva de Potencia vs δ y la curva Potencia vs n.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS
from utils.spc_utils import compute_arl
from utils.widgets import CollapsibleChart


# ── Fórmulas auxiliares ───────────────────────────────────────────────────────

def _power_formula(delta_sigma: float, n: int, k: float = 3.0) -> float:
    """
    Potencia de la carta X̄ con límites k·σ/√n (fórmula estándar).
    Usa la curva OC normal para corrimiento δ (en unidades de σ).
    Sirve para calcular la curva potencia-vs-n con límites ajustados.
    """
    d = abs(float(delta_sigma))
    sqn = np.sqrt(max(n, 1))
    beta = (stats.norm.cdf(k - d * sqn) -
            stats.norm.cdf(-k - d * sqn))
    return float(1.0 - np.clip(beta, 0.0, 1.0))


def _required_n(delta_sigma: float, target_power: float, k: float = 3.0) -> int:
    """
    n mínimo para alcanzar target_power ante un corrimiento |δ_sigma|.
    Fórmula: n = ((k + Z_{1-β}) / |δ_sigma|)²
    """
    if abs(delta_sigma) < 1e-10:
        return 999999
    z1b = stats.norm.ppf(float(np.clip(target_power, 0.001, 0.9999)))
    n_exact = ((k + z1b) / abs(delta_sigma)) ** 2
    return max(1, int(np.ceil(n_exact)))


# ─────────────────────────────────────────────────────────────────────────────
class MejoraModule(tk.Frame):
    """
    Sesión de Plan de Mejora: sensibilidad de la carta X̄ y n óptimo.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._build_ui()

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self, text=(
            "Evalúe la sensibilidad actual del sistema de monitoreo ante corrimientos en la media "
            "y determine el tamaño de muestra necesario para alcanzar la potencia de detección objetivo."
        ), bg=COLORS['bg'], fg=COLORS['text_light'], font=FONTS['small'],
            wraplength=1050, justify='left').pack(fill='x', padx=16, pady=(10, 4))

        paned = tk.PanedWindow(self, orient='horizontal', bg=COLORS['bg'],
                               sashwidth=6, sashrelief='flat')
        paned.pack(fill='both', expand=True, padx=10, pady=4)

        left = tk.Frame(paned, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        paned.add(left, minsize=290, width=320)
        self._build_left(left)

        right = tk.Frame(paned, bg=COLORS['bg'])
        paned.add(right, minsize=580)
        self._build_right(right)

    # ── Panel izquierdo – entradas ────────────────────────────────────────────
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

        # Cabecera
        hdr = tk.Frame(inner, bg=COLORS['primary_light'], pady=6)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Plan de Mejora – Parámetros',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, side='left')

        self._entries = {}

        # ── Sección 1: Parámetros de la carta ────────────────────────────────
        self._section(inner, '1. Parámetros de la Carta X̄', [
            ('X̄̄  (media proceso):', 'xbar',  '3.2400'),
            ('σ  (desv. estándar):', 'sigma', '0.09865'),
            ('n  (tamaño actual):',  'n',     '6'),
            ('t  (intervalo, min):', 't',     '15'),
            ('UCL X̄ (LCS):',        'ucl',   '3.3608'),
            ('LCL X̄ (LCI):',        'lcl',   '3.1192'),
        ])

        # ── Sección 2: Corrimiento a detectar ────────────────────────────────
        sf = tk.LabelFrame(inner, text='2. Corrimiento a Detectar',
                           bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        sf.pack(fill='x', padx=10, pady=(6, 4))
        si = tk.Frame(sf, bg=COLORS['bg_card'])
        si.pack(fill='x', padx=8, pady=6)

        tk.Label(si, text="X̄' (media desplazada):", font=FONTS['small'],
                 bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                     row=0, column=0, sticky='e', padx=(0, 6), pady=3)
        e_xnew = tk.Entry(si, width=11, font=FONTS['entry'], bd=1, relief='solid')
        e_xnew.insert(0, '3.30')
        e_xnew.grid(row=0, column=1, sticky='w', pady=3)
        self._entries['xbar_new'] = e_xnew

        tk.Label(si, text='δ calculado (σ):', font=FONTS['small'],
                 bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                     row=1, column=0, sticky='e', padx=(0, 6), pady=3)
        self._lbl_delta = tk.Label(si, text='—', font=FONTS['label_b'],
                                    bg=COLORS['bg_card'], fg=COLORS['primary'])
        self._lbl_delta.grid(row=1, column=1, sticky='w', pady=3)

        # ── Sección 3: Potencia objetivo ─────────────────────────────────────
        self._section(inner, '3. Potencia Objetivo', [
            ('Potencia objetivo (%):', 'target_power', '98'),
            ('k  (factor límites):',   'k',            '3'),
        ])

        # Botón calcular
        tk.Button(inner, text='▶  Calcular Plan de Mejora',
                  command=self._calculate,
                  bg=COLORS['primary'], fg=COLORS['text_white'],
                  font=FONTS['subheader'], relief='flat', bd=0,
                  cursor='hand2', padx=12, pady=10).pack(
                      fill='x', padx=10, pady=(10, 14))

    def _section(self, parent, title, fields):
        """Crea un LabelFrame con entradas de texto."""
        lf = tk.LabelFrame(parent, text=title,
                           bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['small'])
        lf.pack(fill='x', padx=10, pady=(6, 2))
        fi = tk.Frame(lf, bg=COLORS['bg_card'])
        fi.pack(fill='x', padx=8, pady=6)
        for i, (lbl, key, default) in enumerate(fields):
            tk.Label(fi, text=lbl, font=FONTS['small'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                         row=i, column=0, sticky='e', padx=(0, 6), pady=2)
            e = tk.Entry(fi, width=11, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, default)
            e.grid(row=i, column=1, sticky='w', pady=2)
            self._entries[key] = e

    # ── Panel derecho – resultados y gráficas ─────────────────────────────────
    def _build_right(self, parent):
        scroll_outer = tk.Frame(parent, bg=COLORS['bg'])
        scroll_outer.pack(fill='both', expand=True)

        cv = tk.Canvas(scroll_outer, bg=COLORS['bg'], highlightthickness=0)
        vsb = ttk.Scrollbar(scroll_outer, orient='vertical', command=cv.yview)
        cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        cv.pack(side='left', fill='both', expand=True)

        rf = tk.Frame(cv, bg=COLORS['bg'])
        _cw = cv.create_window((0, 0), window=rf, anchor='nw')
        rf.bind('<Configure>', lambda e: cv.configure(scrollregion=cv.bbox('all')))
        cv.bind('<Configure>', lambda e: cv.itemconfig(_cw, width=e.width))
        cv.bind('<MouseWheel>', lambda e: cv.yview_scroll(int(-1*(e.delta/120)), 'units'))

        self._build_sensitivity_cards(rf)
        self._build_n_cards(rf)
        self._build_procedure_box(rf)
        self._build_charts(rf)

    # ── Tarjetas de sensibilidad actual ──────────────────────────────────────
    def _build_sensitivity_cards(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x', padx=6, pady=(0, 0))
        tk.Label(hdr, text='Evaluación de Sensibilidad Actual',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, anchor='w')

        card = tk.Frame(parent, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        card.pack(fill='x', padx=6, pady=(0, 6))

        row_f = tk.Frame(card, bg=COLORS['bg_card'])
        row_f.pack(fill='x', padx=10, pady=8)

        self._sens = {}
        items = [
            ('power', '1−β  (Potencia)',    '—', COLORS['primary']),
            ('beta',  'β  (No detectar)',   '—', COLORS['danger']),
            ('z_val', 'Z₁₋β',              '—', COLORS['text']),
            ('nrl',   'NRL  (subgrupos)',   '—', COLORS['text']),
            ('ats_m', 'ATS  (minutos)',     '—', COLORS['warning']),
            ('ats_h', 'ATS  (horas)',       '—', COLORS['warning']),
        ]
        for col, (key, label, default, color) in enumerate(items):
            f = tk.Frame(row_f, bg=COLORS['bg_row_alt'],
                         highlightbackground=COLORS['border'], highlightthickness=1)
            f.grid(row=0, column=col, padx=3, pady=2, sticky='ew')
            tk.Label(f, text=label, font=FONTS['small'],
                     bg=COLORS['bg_row_alt'], fg=COLORS['text_light']).pack(padx=6, pady=(4, 0))
            lbl = tk.Label(f, text=default, font=FONTS['result'],
                           bg=COLORS['bg_row_alt'], fg=color)
            lbl.pack(padx=6, pady=(0, 4))
            self._sens[key] = lbl
        for c in range(len(items)):
            row_f.grid_columnconfigure(c, weight=1)

        self._sens_interp = tk.Label(card, text='', font=FONTS['small'],
                                      bg=COLORS['bg_card'], fg=COLORS['text'],
                                      wraplength=750, justify='left')
        self._sens_interp.pack(fill='x', padx=12, pady=(0, 8))

    # ── Tarjetas de n requerido ───────────────────────────────────────────────
    def _build_n_cards(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x', padx=6)
        tk.Label(hdr, text='Tamaño de Muestra para la Potencia Objetivo',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, anchor='w')

        card = tk.Frame(parent, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        card.pack(fill='x', padx=6, pady=(0, 6))

        row_f = tk.Frame(card, bg=COLORS['bg_card'])
        row_f.pack(fill='x', padx=10, pady=8)

        self._nreq = {}
        items = [
            ('n_req',    'n  requerido',          '—', COLORS['primary']),
            ('z1b',      'Z₁₋β  objetivo',        '—', COLORS['text']),
            ('delta_s',  'δ  (unidades σ)',        '—', COLORS['text']),
            ('pwr_curr', 'Potencia  n actual',     '—', COLORS['danger']),
            ('pwr_half', 'Potencia  n intermedio', '—', COLORS['warning']),
        ]
        for col, (key, label, default, color) in enumerate(items):
            f = tk.Frame(row_f, bg=COLORS['bg_row_alt'],
                         highlightbackground=COLORS['border'], highlightthickness=1)
            f.grid(row=0, column=col, padx=3, pady=2, sticky='ew')
            tk.Label(f, text=label, font=FONTS['small'],
                     bg=COLORS['bg_row_alt'], fg=COLORS['text_light']).pack(padx=6, pady=(4, 0))
            lbl = tk.Label(f, text=default, font=FONTS['result'],
                           bg=COLORS['bg_row_alt'], fg=color)
            lbl.pack(padx=6, pady=(0, 4))
            self._nreq[key] = lbl
        for c in range(len(items)):
            row_f.grid_columnconfigure(c, weight=1)

        self._n_interp = tk.Label(card, text='', font=FONTS['small'],
                                   bg=COLORS['bg_card'], fg=COLORS['text'],
                                   wraplength=750, justify='left')
        self._n_interp.pack(fill='x', padx=12, pady=(0, 8))

    # ── Cuadro de procedimiento ───────────────────────────────────────────────
    def _build_procedure_box(self, parent):
        hdr = tk.Frame(parent, bg=COLORS['primary_light'], pady=5)
        hdr.pack(fill='x', padx=6)
        tk.Label(hdr, text='Procedimiento de Cálculo',
                 font=FONTS['subheader'], bg=COLORS['primary_light'],
                 fg=COLORS['text_white']).pack(padx=12, anchor='w')

        card = tk.Frame(parent, bg=COLORS['bg_card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        card.pack(fill='x', padx=6, pady=(0, 6))

        self._proc_txt = tk.Text(card, height=14, font=('Consolas', 9),
                                  bg=COLORS['bg_card'], fg=COLORS['text'],
                                  relief='flat', wrap='word',
                                  state='disabled', padx=12, pady=8)
        self._proc_txt.pack(fill='x')
        self._proc_txt.tag_configure('title', font=('Segoe UI', 9, 'bold'),
                                      foreground=COLORS['primary'])
        self._proc_txt.tag_configure('formula', font=('Consolas', 9),
                                      foreground='#1565C0')
        self._proc_txt.tag_configure('result', font=('Consolas', 9, 'bold'),
                                      foreground=COLORS['danger'])

    # ── Gráficas ──────────────────────────────────────────────────────────────
    def _build_charts(self, parent):
        self._cc_delta = CollapsibleChart(
            parent, 'Curva de Potencia  vs  Corrimiento δ', figsize=(9, 2.8))
        self._cc_delta.pack(fill='x', padx=6, pady=(0, 3))
        self._ax_delta = self._cc_delta.ax

        self._cc_n = CollapsibleChart(
            parent, 'Potencia  vs  Tamaño de Muestra n', figsize=(9, 2.8))
        self._cc_n.pack(fill='x', padx=6, pady=(0, 3))
        self._ax_n = self._cc_n.ax

        self._draw_empty_charts()

    def _draw_empty_charts(self):
        for ax, title in [
            (self._ax_delta, 'Curva de Potencia vs Corrimiento δ'),
            (self._ax_n,     'Potencia vs Tamaño de Muestra n'),
        ]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Ingrese parámetros y presione "Calcular Plan de Mejora"',
                    ha='center', va='center', transform=ax.transAxes,
                    color=COLORS['text_light'], fontsize=9, style='italic')
            ax.tick_params(labelsize=8)
        self._cc_delta.draw()
        self._cc_n.draw()

    # ── Lectura de entradas ───────────────────────────────────────────────────
    def _read(self):
        vals = {}
        for key, e in self._entries.items():
            raw = e.get().replace(',', '.')
            try:
                vals[key] = float(raw)
            except ValueError:
                return None, key
        return vals, None

    # ── Cálculo principal ─────────────────────────────────────────────────────
    def _calculate(self):
        vals, bad = self._read()
        if vals is None:
            messagebox.showwarning('Valor inválido',
                f'El campo "{bad}" no contiene un número válido.')
            return

        xbar        = vals['xbar']
        sigma       = vals['sigma']
        n           = max(1, int(round(vals['n'])))
        t           = vals['t']
        ucl         = vals['ucl']
        lcl         = vals['lcl']
        xbar_new    = vals['xbar_new']
        target_pwr  = vals['target_power'] / 100.0
        k           = vals['k']

        if sigma <= 0:
            messagebox.showwarning('σ inválido', 'La desviación estándar debe ser mayor que 0.')
            return
        if not (0.01 < target_pwr < 0.9999):
            messagebox.showwarning('Potencia inválida',
                'La potencia objetivo debe estar entre 1% y 99.99%.')
            return

        delta       = xbar_new - xbar            # corrimiento real
        delta_sigma = delta / sigma              # corrimiento en unidades de σ

        self._lbl_delta.configure(text=f'{delta_sigma:+.4f} σ')

        # ── Potencia actual (con UCL/LCL reales) ─────────────────────────────
        r = compute_arl(ucl, lcl, xbar, sigma, n, delta=delta)
        power   = r['poder']
        beta    = r['beta']
        nrl     = r['arl']
        ats_min = nrl * t
        ats_h   = ats_min / 60.0

        if 0 < power < 1:
            z_val = stats.norm.ppf(power)
        else:
            z_val = float('inf') if power >= 1 else float('-inf')

        pwr_col = (COLORS['success'] if power >= 0.90
                   else COLORS['warning'] if power >= 0.50
                   else COLORS['danger'])

        self._sens['power'].configure(text=f'{power*100:.2f}%',  fg=pwr_col)
        self._sens['beta'].configure( text=f'{beta*100:.2f}%')
        self._sens['z_val'].configure(text=f'{z_val:.4f}')
        self._sens['nrl'].configure(  text=f'{nrl:.2f}' if nrl < 99999 else '∞')
        self._sens['ats_m'].configure(text=f'{ats_min:.1f} min')
        self._sens['ats_h'].configure(text=f'{ats_h:.2f} h')

        dir_txt = 'incremento' if delta > 0 else 'reducción'
        self._sens_interp.configure(text=(
            f"Ante un {dir_txt} de la media de {abs(delta):.5f} unidades "
            f"(δ = {abs(delta_sigma):.4f} σ), la carta X̄ con n = {n} detecta el "
            f"corrimiento en promedio cada {nrl:.1f} subgrupos, equivalente a "
            f"{ats_h:.2f} horas de operación continua."
        ))

        # ── n requerido ───────────────────────────────────────────────────────
        n_req = _required_n(delta_sigma, target_pwr, k)
        z1b   = stats.norm.ppf(target_pwr)

        # Potencia con n intermedio (mitad del camino entre actual y requerido)
        n_half = max(1, (n + n_req) // 2)
        pwr_half = _power_formula(delta_sigma, n_half, k)

        n_col = COLORS['primary'] if n_req <= n * 4 else COLORS['danger']
        pwr_h_col = (COLORS['success'] if pwr_half >= 0.90
                     else COLORS['warning'] if pwr_half >= 0.50
                     else COLORS['danger'])

        self._nreq['n_req'].configure(   text=str(n_req),                fg=n_col)
        self._nreq['z1b'].configure(     text=f'{z1b:.4f}')
        self._nreq['delta_s'].configure( text=f'{abs(delta_sigma):.4f} σ')
        self._nreq['pwr_curr'].configure(text=f'{power*100:.2f}%  (n={n})',  fg=pwr_col)
        self._nreq['pwr_half'].configure(text=f'{pwr_half*100:.2f}%  (n={n_half})', fg=pwr_h_col)

        self._n_interp.configure(text=(
            f"Para alcanzar una potencia del {target_pwr*100:.0f}% ante un corrimiento "
            f"de δ = {abs(delta_sigma):.4f} σ se requiere n = {n_req} "
            f"(actualmente n = {n}). "
            + ("Este tamaño puede ser poco práctico operativamente; "
               "se recomienda también reducir σ del proceso."
               if n_req > 30 else
               f"Con n = {n_half} (intermedio) se lograría una potencia del {pwr_half*100:.1f}%.")
        ))

        # ── Procedimiento de cálculo ──────────────────────────────────────────
        self._update_procedure(
            xbar, sigma, n, t, ucl, lcl, xbar_new,
            delta, delta_sigma, z_val, power, beta, nrl, ats_min, ats_h,
            target_pwr, z1b, k, n_req
        )

        # ── Gráfica 1: Potencia vs δ ──────────────────────────────────────────
        d_range = np.linspace(0, max(4.0, abs(delta_sigma) * 2.5), 400)
        pwrs_d  = [_power_formula(d, n, k) * 100 for d in d_range]

        ax1 = self._ax_delta
        ax1.clear()
        ax1.set_facecolor('#FAFAFA')
        ax1.plot(d_range, pwrs_d, color=COLORS['primary'], lw=2, label=f'n = {n}')
        ax1.fill_between(d_range, pwrs_d, alpha=0.10, color=COLORS['primary'])
        ax1.axvline(abs(delta_sigma), color=COLORS['danger'], lw=1.5, ls='--',
                    label=f'δ = {abs(delta_sigma):.2f}σ  →  {power*100:.1f}%')
        ax1.axhline(target_pwr * 100, color=COLORS['warning'], lw=1.2, ls=':',
                    label=f'Objetivo {target_pwr*100:.0f}%')
        ax1.axhline(90, color=COLORS['chart_ucl'], lw=1.0, ls=':', alpha=0.7, label='90%')
        ax1.scatter([abs(delta_sigma)], [power * 100],
                    color=COLORS['danger'], s=55, zorder=5)
        ax1.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
        ax1.set_ylabel('Potencia (%)', fontsize=8)
        ax1.set_title(f'Curva de Potencia – Carta X̄  (n = {n})',
                      fontsize=10, fontweight='bold', color=COLORS['text'])
        ax1.set_ylim(-2, 107)
        ax1.tick_params(labelsize=8)
        ax1.legend(fontsize=7, loc='lower right')
        ax1.grid(True, alpha=0.3, ls=':')
        self._cc_delta.fig.tight_layout(pad=1.2)
        self._cc_delta.draw()

        # ── Gráfica 2: Potencia vs n ──────────────────────────────────────────
        n_max   = max(n_req + max(n_req // 2, 5), n * 3, 20)
        n_range = np.arange(1, n_max + 1)
        pwrs_n  = [_power_formula(delta_sigma, int(ni), k) * 100 for ni in n_range]

        ax2 = self._ax_n
        ax2.clear()
        ax2.set_facecolor('#FAFAFA')
        ax2.plot(n_range, pwrs_n, color=COLORS['primary'], lw=2)
        ax2.fill_between(n_range, pwrs_n, alpha=0.10, color=COLORS['primary'])
        ax2.axvline(n, color=COLORS['chart_data'], lw=1.5, ls='--',
                    label=f'n actual = {n}  →  {power*100:.1f}%')
        ax2.axvline(n_req, color=COLORS['danger'], lw=1.5, ls='--',
                    label=f'n requerido = {n_req}  →  {target_pwr*100:.0f}%')
        ax2.axhline(target_pwr * 100, color=COLORS['warning'], lw=1.2, ls=':',
                    label=f'Objetivo {target_pwr*100:.0f}%')
        ax2.axhline(90, color=COLORS['chart_ucl'], lw=1.0, ls=':', alpha=0.7, label='90%')
        ax2.scatter([n],     [power * 100],     color=COLORS['chart_data'], s=55, zorder=5)
        ax2.scatter([n_req], [target_pwr * 100], color=COLORS['danger'],    s=55, zorder=5)
        ax2.set_xlabel('Tamaño de subgrupo n', fontsize=8)
        ax2.set_ylabel('Potencia (%)', fontsize=8)
        ax2.set_title(f'Potencia vs n  |  δ = {abs(delta_sigma):.2f}σ',
                      fontsize=10, fontweight='bold', color=COLORS['text'])
        ax2.set_ylim(-2, 107)
        ax2.set_xlim(0, n_max + 1)
        ax2.tick_params(labelsize=8)
        ax2.legend(fontsize=7, loc='lower right')
        ax2.grid(True, alpha=0.3, ls=':')
        self._cc_n.fig.tight_layout(pad=1.2)
        self._cc_n.draw()

    # ── Procedimiento paso a paso ─────────────────────────────────────────────
    def _update_procedure(self, xbar, sigma, n, t, ucl, lcl, xbar_new,
                          delta, delta_sigma, z_val, power, beta,
                          nrl, ats_min, ats_h,
                          target_pwr, z1b, k, n_req):
        se = sigma / np.sqrt(n)
        z_ucl = (ucl - xbar_new) / se
        z_lcl = (lcl - xbar_new) / se

        lines = []

        lines.append(('title', '─── A. Evaluación de Sensibilidad Actual ─────────────────\n'))
        lines.append(('text',  f'Parámetros: X̄̄ = {xbar}, σ = {sigma}, n = {n}, '
                                f'UCL = {ucl}, LCL = {lcl}\n'))
        lines.append(('text',  f'Media a detectar: X̄\' = {xbar_new}\n\n'))

        lines.append(('text',  'Error estándar de la media:\n'))
        lines.append(('formula', f'   σ/√n = {sigma} / √{n} = {se:.6f}\n\n'))

        lines.append(('text',  'Argumentos Z para la función normal:\n'))
        lines.append(('formula',
            f'   Z_sup = (UCL − X̄\') / (σ/√n) = ({ucl} − {xbar_new}) / {se:.6f} = {z_ucl:.4f}\n'))
        lines.append(('formula',
            f'   Z_inf = (LCL − X̄\') / (σ/√n) = ({lcl} − {xbar_new}) / {se:.6f} = {z_lcl:.4f}\n\n'))

        lines.append(('text',  'Probabilidad de NO detectar (β):\n'))
        lines.append(('formula',
            f'   β = Φ({z_ucl:.4f}) − Φ({z_lcl:.4f})\n'))
        lines.append(('formula',
            f'     = {stats.norm.cdf(z_ucl):.6f} − {stats.norm.cdf(z_lcl):.6f}\n'))
        lines.append(('result', f'     = {beta:.6f}  →  β = {beta*100:.2f}%\n\n'))

        lines.append(('text',  'Potencia del gráfico:\n'))
        lines.append(('formula', f'   1 − β = 1 − {beta:.6f}'))
        lines.append(('result',  f' = {power:.6f}  →  {power*100:.2f}%\n\n'))

        lines.append(('text',  'NRL (número de muestras hasta detectar):\n'))
        lines.append(('formula', f'   NRL = 1 / (1−β) = 1 / {power:.6f}'))
        lines.append(('result',  f' = {nrl:.2f} subgrupos\n\n'))

        lines.append(('text',  'ATS (tiempo promedio de señal):\n'))
        lines.append(('formula', f'   ATS = NRL × t = {nrl:.2f} × {t} min'))
        lines.append(('result',  f' = {ats_min:.1f} min  →  {ats_h:.2f} horas\n\n'))

        lines.append(('title', '─── B. Tamaño de Muestra para Potencia Objetivo ──────────\n'))
        lines.append(('text',  f'Potencia objetivo: 1−β = {target_pwr*100:.0f}%   '
                                f'→  Z_{{1−β}} = {z1b:.4f}\n'))
        lines.append(('text',  f'Factor de límites: k = Zα/2 = {k}\n'))
        lines.append(('text',  f'Corrimiento: δ = |X̄\' − X̄̄| / σ = |{xbar_new} − {xbar}| / {sigma} = {abs(delta_sigma):.4f} σ\n\n'))

        lines.append(('text',  'Fórmula:\n'))
        lines.append(('formula',
            f'   n = ( (k + Z_{{1−β}}) / δ_σ )²\n'))
        lines.append(('formula',
            f'     = ( ({k} + {z1b:.4f}) / {abs(delta_sigma):.4f} )²\n'))
        lines.append(('formula',
            f'     = ( {k + z1b:.4f} / {abs(delta_sigma):.4f} )²\n'))
        lines.append(('formula',
            f'     = {(k + z1b) / abs(delta_sigma):.4f}²\n'))
        lines.append(('result',  f'     ≈ {((k + z1b) / abs(delta_sigma))**2:.2f}  →  n = {n_req}\n'))

        # Escribir en el widget Text
        txt = self._proc_txt
        txt.configure(state='normal')
        txt.delete('1.0', 'end')
        for tag, content in lines:
            txt.insert('end', content, tag if tag != 'text' else '')
        txt.configure(state='disabled')
