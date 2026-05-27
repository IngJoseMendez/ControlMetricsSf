# -*- coding: utf-8 -*-
"""
Módulo: Plan de Muestreo por Aceptación (MIL-STD-105E / ANSI Z1.4)
Sistema SPC – PMD y Cía S.C.A.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS, DEFAULTS, MILSTD_CODE_LETTER, MILSTD_PLANS
from utils.spc_utils import compute_oc_curve, parse_value, milstd_code_letter, milstd_plan
from utils.widgets import CollapsibleChart


class MuestreoModule(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._build_ui()

    def _build_ui(self):
        inst = tk.Label(self, text=(
            "Diseñe el plan de muestreo por aceptación para inspección en puerto. "
            "Basado en MIL-STD-105E / ANSI/ASQ Z1.4. Lote estándar: 20 pallets × 48 cajas = 960 cajas. NAC = 4%."
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
        tk.Label(hdr, text='Parámetros del Plan', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='both', expand=True, padx=10, pady=8)

        # Parámetros del lote
        lote_f = tk.LabelFrame(body, text='Parámetros del Lote',
                               bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['label_b'])
        lote_f.pack(fill='x', pady=(0, 8))

        lote_fields = [
            ('Tamaño del lote (N):', 'n_lote', '960'),
            ('N° de pallets:', 'n_pallets', '20'),
            ('Cajas por pallet:', 'cajas_pallet', '48'),
        ]
        self.lote_entries = {}
        for i, (lbl, key, val) in enumerate(lote_fields):
            tk.Label(lote_f, text=lbl, font=FONTS['label_b'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light'], anchor='e',
                     width=22).grid(row=i, column=0, sticky='e', padx=(8, 4), pady=4)
            e = tk.Entry(lote_f, width=10, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, val)
            e.grid(row=i, column=1, sticky='w', padx=(0, 8), pady=4)
            self.lote_entries[key] = e

        # Botón calcular tamaño de lote
        tk.Button(lote_f, text='Recalcular lote (pallets × cajas)',
                  command=self._recalc_lote, bg=COLORS['bg_row_alt'],
                  fg=COLORS['text'], font=FONTS['small'], relief='flat',
                  cursor='hand2', padx=6, pady=3).grid(
                      row=3, column=0, columnspan=2, padx=8, pady=4, sticky='ew')

        # Parámetros del plan
        plan_f = tk.LabelFrame(body, text='Parámetros de Inspección (MIL-STD-105E)',
                               bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['label_b'])
        plan_f.pack(fill='x', pady=(0, 8))

        plan_fields = [
            ('NAC / AQL (%):', 'nac', '4.0'),
        ]
        self.plan_entries = {}
        for i, (lbl, key, val) in enumerate(plan_fields):
            tk.Label(plan_f, text=lbl, font=FONTS['label_b'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light'], anchor='e',
                     width=22).grid(row=i, column=0, sticky='e', padx=(8, 4), pady=4)
            e = tk.Entry(plan_f, width=10, font=FONTS['entry'], bd=1, relief='solid')
            e.insert(0, val)
            e.grid(row=i, column=1, sticky='w', padx=(0, 8), pady=4)
            self.plan_entries[key] = e

        # Nivel de inspección
        tk.Label(plan_f, text='Nivel de inspección:', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text_light'], anchor='e',
                 width=22).grid(row=1, column=0, sticky='e', padx=(8, 4), pady=4)
        self.nivel_var = tk.StringVar(value='II')
        ttk.Combobox(plan_f, textvariable=self.nivel_var, width=8, state='readonly',
                     values=['I', 'II', 'III']).grid(row=1, column=1, sticky='w', padx=(0, 8), pady=4)

        # Tipo de inspección
        tk.Label(plan_f, text='Tipo de inspección:', font=FONTS['label_b'],
                 bg=COLORS['bg_card'], fg=COLORS['text_light'], anchor='e',
                 width=22).grid(row=2, column=0, sticky='e', padx=(8, 4), pady=4)
        self.tipo_var = tk.StringVar(value='Normal')
        ttk.Combobox(plan_f, textvariable=self.tipo_var, width=12, state='readonly',
                     values=['Normal', 'Estricta', 'Reducida']).grid(
                         row=2, column=1, sticky='w', padx=(0, 8), pady=4)

        # Plan manual (override)
        manual_f = tk.LabelFrame(body, text='Plan Personalizado (override)',
                                 bg=COLORS['bg_card'], fg=COLORS['text'], font=FONTS['label_b'])
        manual_f.pack(fill='x', pady=(0, 8))

        self.use_manual = tk.BooleanVar(value=False)
        tk.Checkbutton(manual_f, text='Usar plan personalizado',
                       variable=self.use_manual, bg=COLORS['bg_card'],
                       font=FONTS['small'], command=self._toggle_manual).pack(
                           anchor='w', padx=8, pady=(4, 0))

        man_inner = tk.Frame(manual_f, bg=COLORS['bg_card'])
        man_inner.pack(fill='x', padx=8, pady=(0, 6))
        self.manual_entries = {}
        for i, (lbl, key, val) in enumerate([
            ('n (muestra):', 'n_plan', '80'),
            ('c (Ac):', 'c_plan', '7'),
        ]):
            tk.Label(man_inner, text=lbl, font=FONTS['label_b'],
                     bg=COLORS['bg_card'], fg=COLORS['text_light']).grid(
                         row=0, column=i*2, padx=(0, 4))
            e = tk.Entry(man_inner, width=7, font=FONTS['entry'], bd=1,
                         relief='solid', state='disabled')
            e.insert(0, val)
            e.grid(row=0, column=i*2+1, padx=(0, 10))
            self.manual_entries[key] = e

        # Botones
        btn_f = tk.Frame(body, bg=COLORS['bg_card'])
        btn_f.pack(fill='x', pady=(6, 2))
        btns = [
            ('Calcular plan', self._run, COLORS['primary'], COLORS['text_white']),
            ('Plan del estudio', self._load_demo, COLORS['secondary'], COLORS['text']),
            ('Limpiar', self._clear, '#CFD8DC', COLORS['text']),
        ]
        for txt, cmd, bg, fg in btns:
            tk.Button(btn_f, text=txt, command=cmd, bg=bg, fg=fg,
                      font=FONTS['label_b'], relief='flat', bd=0,
                      cursor='hand2', padx=8, pady=5).pack(side='left', padx=3)

        # Sección Excel
        tk.Frame(body, bg=COLORS['border'], height=1).pack(fill='x', pady=(4, 2))
        tk.Label(body,
                 text='📋 Excel: col. A = parámetro, col. B = valor\n'
                      '   Claves: n_lote, pallets, cajas_pallet, nac',
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['text_light'], justify='left').pack(anchor='w')
        excel_row = tk.Frame(body, bg=COLORS['bg_card'])
        excel_row.pack(fill='x', pady=2)
        tk.Button(excel_row, text='📂 Cargar desde Excel', command=self._load_excel,
                  bg='#0277BD', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(
                      side='left', fill='x', expand=True, padx=(0, 3))
        tk.Button(excel_row, text='📄 Plantilla', command=self._gen_template,
                  bg='#37474F', fg=COLORS['text_white'], font=FONTS['label_b'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=5).pack(side='left')

    def _toggle_manual(self):
        state = 'normal' if self.use_manual.get() else 'disabled'
        for e in self.manual_entries.values():
            e.configure(state=state)

    def _recalc_lote(self):
        try:
            pallets = int(self.lote_entries['n_pallets'].get())
            cajas   = int(self.lote_entries['cajas_pallet'].get())
            total = pallets * cajas
            self.lote_entries['n_lote'].delete(0, 'end')
            self.lote_entries['n_lote'].insert(0, str(total))
        except Exception:
            pass

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
        tk.Label(hdr, text='Resultado del Plan de Muestreo', font=FONTS['subheader'],
                 bg=COLORS['primary_light'], fg=COLORS['text_white']).pack(padx=12, anchor='w')

        body = tk.Frame(parent, bg=COLORS['bg_card'])
        body.pack(fill='x', padx=10, pady=8)

        self.res_labels = {}

        # Fila 1: Plan
        row1 = tk.Frame(body, bg=COLORS['bg_card'])
        row1.pack(fill='x', pady=2)
        plan_cards = [
            ('Letra Código', 'letra', COLORS['primary']),
            ('Tamaño muestra (n)', 'n', COLORS['primary_light']),
            ('Ac (aceptar si ≤)', 'ac', COLORS['info']),
            ('Re (rechazar si ≥)', 're', COLORS['danger']),
        ]
        for lbl, key, color in plan_cards:
            f = tk.Frame(row1, bg=color)
            f.pack(side='left', padx=6, pady=2, ipadx=14, ipady=8)
            tk.Label(f, text=lbl, font=FONTS['small'],
                     bg=color, fg=COLORS['text_white']).pack()
            lb = tk.Label(f, text='—', font=('Segoe UI', 18, 'bold'),
                          bg=color, fg=COLORS['text_white'], width=7)
            lb.pack()
            self.res_labels[key] = lb

        # Fila 2: Riesgos
        row2 = tk.Frame(body, bg=COLORS['bg_card'])
        row2.pack(fill='x', pady=2)
        risk_fields = [
            ('Riesgo proveedor (α) @ NAC:', 'alpha_risk'),
            ('Riesgo cliente (β) @ 2×NAC:', 'beta_risk'),
            ('Pa @ p=0% (ideal):', 'pa_0'),
            ('Pa @ NAC:', 'pa_nac'),
            ('Pa @ 2×NAC:', 'pa_2nac'),
        ]
        for lbl, key in risk_fields:
            f = tk.Frame(row2, bg=COLORS['secondary_light'], bd=0,
                         highlightbackground=COLORS['secondary'], highlightthickness=1)
            f.pack(side='left', padx=4, pady=2, ipadx=6, ipady=4)
            tk.Label(f, text=lbl, font=FONTS['small'],
                     bg=COLORS['secondary_light'], fg=COLORS['text_light']).pack()
            lb = tk.Label(f, text='—', font=FONTS['result'],
                          bg=COLORS['secondary_light'], fg=COLORS['text'], width=10)
            lb.pack()
            self.res_labels[key] = lb

        self.eval_muestreo = tk.Label(body, text='', font=FONTS['label_b'],
                                      bg=COLORS['bg_card'], fg=COLORS['text'])
        self.eval_muestreo.pack(anchor='w', padx=4, pady=(4, 0))

    def _build_charts(self, parent):
        self._cc_oc = CollapsibleChart(
            parent, 'Curva Característica de Operación (OC)', figsize=(6, 3.5))
        self._cc_oc.pack(side='left', fill='both', expand=True, padx=(0, 2))
        self.ax_oc = self._cc_oc.ax

        self._cc_aoq = CollapsibleChart(
            parent, 'Curva de Calidad Promedio de Salida (AOQ)', figsize=(6, 3.5))
        self._cc_aoq.pack(side='left', fill='both', expand=True, padx=(2, 0))
        self.ax_aoq = self._cc_aoq.ax

        self._draw_empty()

    def _draw_all(self):
        self._cc_oc.fig.tight_layout(pad=1.5)
        self._cc_aoq.fig.tight_layout(pad=1.5)
        self._cc_oc.draw()
        self._cc_aoq.draw()

    def _draw_empty(self):
        for ax, title in [(self.ax_oc, 'Curva Característica de Operación (OC)'),
                          (self.ax_aoq, 'Curva de Calidad Promedio de Salida (AOQ)')]:
            ax.clear()
            ax.set_facecolor('#FAFAFA')
            ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                    transform=ax.transAxes, color=COLORS['text_light'], fontsize=10)
        self._draw_all()

    # ── Lógica ───────────────────────────────────────────────────────────────
    def _run(self):
        try:
            n_lote = int(parse_value(self.lote_entries['n_lote'].get()) or 960)
            nac_pct = parse_value(self.plan_entries['nac'].get())
            if nac_pct is None:
                messagebox.showerror('Error', 'Ingrese un NAC válido.')
                return
            nac = nac_pct / 100.0

            if self.use_manual.get():
                n_plan = int(parse_value(self.manual_entries['n_plan'].get()) or 80)
                c_plan = int(parse_value(self.manual_entries['c_plan'].get()) or 7)
                letter = milstd_code_letter(n_lote)
            else:
                letter, (n_plan, c_plan, _) = milstd_plan(n_lote)

            re_plan = c_plan + 1

            # Cálculos OC
            p_range = np.linspace(0, 0.35, 500)
            pa = stats.binom.cdf(c_plan, n_plan, p_range)

            # Riesgos
            pa_nac  = float(stats.binom.cdf(c_plan, n_plan, nac))
            pa_2nac = float(stats.binom.cdf(c_plan, n_plan, min(2*nac, 0.999)))
            pa_0    = float(stats.binom.cdf(c_plan, n_plan, 0.0001))
            alpha_r = 1 - pa_nac   # riesgo proveedor
            beta_r  = pa_2nac      # riesgo cliente

            self._update_results(letter, n_plan, c_plan, re_plan,
                                 alpha_r, beta_r, pa_nac, pa_2nac, pa_0)

            # AOQ
            aoq = p_range * pa * (n_lote - n_plan) / n_lote

            self._draw_charts(p_range, pa, aoq, nac, pa_nac, n_plan, c_plan)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _update_results(self, letter, n, c, re, alpha_r, beta_r, pa_nac, pa_2nac, pa_0):
        self.res_labels['letra'].configure(text=letter)
        self.res_labels['n'].configure(text=str(n))
        self.res_labels['ac'].configure(text=str(c))
        self.res_labels['re'].configure(text=str(re))
        self.res_labels['alpha_risk'].configure(text=f'{alpha_r*100:.2f}%')
        self.res_labels['beta_risk'].configure(text=f'{beta_r*100:.2f}%')
        self.res_labels['pa_0'].configure(text=f'{pa_0*100:.1f}%')
        self.res_labels['pa_nac'].configure(text=f'{pa_nac*100:.1f}%')
        self.res_labels['pa_2nac'].configure(text=f'{pa_2nac*100:.1f}%')

        msg = (f'Plan: n={n}, Ac={c}, Re={re}  ·  '
               f'Riesgo proveedor={alpha_r*100:.1f}%  ·  '
               f'Riesgo cliente={beta_r*100:.1f}%')
        self.eval_muestreo.configure(text=msg, fg=COLORS['primary'])

    def _draw_charts(self, p_range, pa, aoq, nac, pa_nac, n_plan, c_plan):
        # ── Curva OC ──
        ax = self.ax_oc
        ax.clear()
        ax.set_facecolor('#FAFAFA')

        ax.plot(p_range*100, pa*100, color=COLORS['primary'], linewidth=2.5, label=f'OC (n={n_plan}, c={c_plan})')
        # Punto NAC
        ax.plot(nac*100, pa_nac*100, 'o', color=COLORS['secondary'], markersize=9,
                zorder=5, label=f'NAC={nac*100:.1f}%  Pa={pa_nac*100:.1f}%')
        ax.axvline(nac*100, color=COLORS['secondary'], linewidth=1.2, linestyle='--', alpha=0.7)
        ax.axhline(pa_nac*100, color=COLORS['secondary'], linewidth=1.0, linestyle=':', alpha=0.7)

        # Zona aceptable
        ax.fill_between(p_range*100, pa*100, alpha=0.08, color=COLORS['primary_lighter'],
                        label='Zona de aceptación')
        ax.axhline(95, color=COLORS['danger'], linewidth=0.8, linestyle=':', alpha=0.5, label='95%')
        ax.axhline(10, color=COLORS['warning'], linewidth=0.8, linestyle=':', alpha=0.5, label='10%')

        ax.set_xlabel('Proporción de defectuosos p (%)', fontsize=9)
        ax.set_ylabel('Probabilidad de Aceptación Pa (%)', fontsize=9)
        ax.set_title(f'Curva OC  –  Plan n={n_plan}, Ac={c_plan}', fontsize=10, fontweight='bold')
        ax.set_xlim(0, p_range[-1]*100)
        ax.set_ylim(0, 105)
        ax.legend(fontsize=7.5)
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.tick_params(labelsize=8)

        # ── Curva AOQ ──
        ax2 = self.ax_aoq
        ax2.clear()
        ax2.set_facecolor('#FAFAFA')

        ax2.plot(p_range*100, aoq*100, color=COLORS['accent'], linewidth=2.5,
                 label='AOQ')
        aoq_max = np.max(aoq)
        p_aoq_max = p_range[np.argmax(aoq)]
        ax2.axvline(p_aoq_max*100, color=COLORS['danger'], linewidth=1.2,
                    linestyle='--', label=f'AOQL = {aoq_max*100:.2f}%')
        ax2.plot(p_aoq_max*100, aoq_max*100, 'o', color=COLORS['danger'], markersize=8, zorder=5)

        ax2.set_xlabel('Proporción de defectuosos p (%)', fontsize=9)
        ax2.set_ylabel('AOQ (%)', fontsize=9)
        ax2.set_title('Calidad Promedio de Salida (AOQ)', fontsize=10, fontweight='bold')
        ax2.set_xlim(0, p_range[-1]*100)
        ax2.legend(fontsize=7.5)
        ax2.grid(True, alpha=0.3, linestyle=':')
        ax2.tick_params(labelsize=8)

        self._draw_all()

    def _load_excel(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_read_muestreo
        fp = filedialog.askopenfilename(
            title='Seleccionar archivo Excel – Parámetros de muestreo',
            filetypes=[('Excel', '*.xlsx *.xls'), ('Todos', '*.*')])
        if not fp:
            return
        try:
            params = excel_read_muestreo(fp)
            if not params:
                messagebox.showwarning('Sin datos',
                    'No se encontraron parámetros.\n'
                    'Formato: col. A = nombre (n_lote, pallets, cajas_pallet, nac), col. B = valor.')
                return
            # Mapeo de claves reconocidas
            key_map = {
                'n_lote': ('n_lote', self.lote_entries),
                'lote': ('n_lote', self.lote_entries),
                'pallets': ('n_pallets', self.lote_entries),
                'n_pallets': ('n_pallets', self.lote_entries),
                'cajas_pallet': ('cajas_pallet', self.lote_entries),
                'cajas_por_pallet': ('cajas_pallet', self.lote_entries),
                'nac': ('nac', self.plan_entries),
                'aql': ('nac', self.plan_entries),
                'nac_pct': ('nac', self.plan_entries),
            }
            loaded = []
            for raw_key, val in params.items():
                mapped = key_map.get(raw_key)
                if mapped:
                    field_key, entries_dict = mapped
                    if field_key in entries_dict:
                        entries_dict[field_key].delete(0, 'end')
                        entries_dict[field_key].insert(0, str(val))
                        loaded.append(f'{raw_key} = {val}')
            if loaded:
                messagebox.showinfo('Excel cargado',
                    'Parámetros cargados:\n• ' + '\n• '.join(loaded))
            else:
                messagebox.showwarning('Sin coincidencias',
                    'No se reconoció ningún parámetro.\n'
                    'Use: n_lote, pallets, cajas_pallet, nac.')
        except Exception as e:
            messagebox.showerror('Error al leer Excel', str(e))

    def _gen_template(self):
        from tkinter import filedialog
        from utils.spc_utils import excel_create_template
        fp = filedialog.asksaveasfilename(
            title='Guardar plantilla Excel',
            defaultextension='.xlsx',
            initialfile='Plantilla_Muestreo.xlsx',
            filetypes=[('Excel', '*.xlsx')])
        if not fp:
            return
        try:
            excel_create_template(fp, 'muestreo')
            messagebox.showinfo('Plantilla creada',
                f'Plantilla guardada en:\n{fp}\n\n'
                'Claves válidas: n_lote, pallets, cajas_pallet, nac.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _load_demo(self):
        self.lote_entries['n_lote'].delete(0, 'end')
        self.lote_entries['n_lote'].insert(0, '960')
        self.lote_entries['n_pallets'].delete(0, 'end')
        self.lote_entries['n_pallets'].insert(0, '20')
        self.lote_entries['cajas_pallet'].delete(0, 'end')
        self.lote_entries['cajas_pallet'].insert(0, '48')
        self.plan_entries['nac'].delete(0, 'end')
        self.plan_entries['nac'].insert(0, '4.0')
        self.nivel_var.set('II')
        self.tipo_var.set('Normal')
        self.use_manual.set(False)
        self._toggle_manual()

    def _clear(self):
        for e in self.lote_entries.values():
            e.delete(0, 'end')
        for e in self.plan_entries.values():
            e.delete(0, 'end')
        for lb in self.res_labels.values():
            lb.configure(text='—')
        self.eval_muestreo.configure(text='')
        self._draw_empty()
