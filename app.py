# -*- coding: utf-8 -*-
"""
Aplicación principal – ControlMetrics
PMD y Cía S.C.A. | Sistema de Control Estadístico de Procesos
"""
import tkinter as tk
from tkinter import ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import COLORS, FONTS, COMPANY
from modules.normalidad   import NormalidadModule
from modules.cartas_xr    import CartasXRModule
from modules.cartas_pnpu  import CartasPNPUModule
from modules.carta_c      import CartaCModule
from modules.capacidad    import CapacidadModule
from modules.muestreo     import MuestreoModule
from modules.mejora       import MejoraModule


class SPCApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{COMPANY['software_name']} – {COMPANY['name']}")
        self.root.state('zoomed')          # ventana maximizada
        self.root.configure(bg=COLORS['bg'])
        self._apply_styles()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

    # ── Estilos ttk ──────────────────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure('TNotebook', background=COLORS['bg'],
                        borderwidth=0, tabmargins=[2, 4, 2, 0])
        style.configure('TNotebook.Tab',
                        background=COLORS['bg_dark'] if 'bg_dark' in COLORS else '#CFD8DC',
                        foreground=COLORS['text'],
                        padding=[18, 8],
                        font=FONTS['label_b'])
        style.map('TNotebook.Tab',
                  background=[('selected', COLORS['primary_light']),
                               ('active',   COLORS['primary_lighter'])],
                  foreground=[('selected', COLORS['text_white']),
                               ('active',   COLORS['text_white'])])

        style.configure('TScrollbar', background=COLORS['border'],
                        troughcolor=COLORS['bg'], width=10)
        style.configure('TCombobox', fieldbackground=COLORS['bg_card'],
                        background=COLORS['bg_card'], foreground=COLORS['text'])
        style.configure('TSpinbox', fieldbackground=COLORS['bg_card'],
                        background=COLORS['bg_card'], foreground=COLORS['text'])

    # ── Cabecera ─────────────────────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS['bg_header'], height=72)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)

        # Icono / Logo texto
        logo_frame = tk.Frame(header, bg=COLORS['primary_lighter'], width=60, height=72)
        logo_frame.pack(side='left', fill='y')
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text='🍌', font=('Segoe UI Emoji', 22),
                 bg=COLORS['primary_lighter'], fg=COLORS['text_white']).place(relx=0.5, rely=0.5, anchor='center')

        # Información de empresa
        info = tk.Frame(header, bg=COLORS['bg_header'])
        info.pack(side='left', fill='y', padx=16)
        tk.Label(info, text=COMPANY['software_name'], font=FONTS['title'],
                 bg=COLORS['bg_header'], fg=COLORS['text_white']).pack(anchor='w', pady=(10, 0))
        subtitle = (f"{COMPANY['name']}  ·  {COMPANY['product']}  ·  "
                    f"{COMPANY['location']}")
        tk.Label(info, text=subtitle, font=FONTS['label'],
                 bg=COLORS['bg_header'], fg='#A5D6A7').pack(anchor='w')

        # Versión
        tk.Label(header, text=f"v{COMPANY['version']}",
                 font=FONTS['small'], bg=COLORS['bg_header'], fg='#81C784').pack(
                     side='right', padx=18, pady=10, anchor='ne')

        # Separador amarillo
        sep = tk.Frame(self.root, bg=COLORS['secondary'], height=4)
        sep.pack(fill='x', side='top')

    # ── Notebook ─────────────────────────────────────────────────────────────
    def _build_notebook(self):
        nb_frame = tk.Frame(self.root, bg=COLORS['bg'])
        nb_frame.pack(fill='both', expand=True, padx=0, pady=0)

        self.notebook = ttk.Notebook(nb_frame)
        self.notebook.pack(fill='both', expand=True, padx=6, pady=6)

        tabs = [
            ('📊  Normalidad',          NormalidadModule),
            ('📈  Cartas X̄ – R',         CartasXRModule),
            ('🔵  Cartas p / np / u',    CartasPNPUModule),
            ('📉  Carta C / Pareto',     CartaCModule),
            ('⚙️  Capacidad (Cp/Cpk)',   CapacidadModule),
            ('🔍  Plan de Muestreo',     MuestreoModule),
            ('🔧  Plan de Mejora',        MejoraModule),
        ]

        for label, ModClass in tabs:
            frame = ModClass(self.notebook)
            self.notebook.add(frame, text=label)

    # ── Barra de estado ───────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=COLORS['primary'], height=24)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)
        tk.Label(bar,
                 text=(f"  {COMPANY['software_name']}  ·  {COMPANY['name']}  ·  "
                       f"Control Estadístico de Procesos  ·  Universidad del Magdalena, 2025"),
                 bg=COLORS['primary'], fg='#C8E6C9', font=FONTS['small']).pack(
                     side='left', padx=8, pady=3)
        tk.Label(bar, text=f"Montgomery (2020)  |  MIL-STD-105E  |  ISO 9001",
                 bg=COLORS['primary'], fg='#A5D6A7', font=FONTS['small']).pack(
                     side='right', padx=8, pady=3)

    def run(self):
        self.root.mainloop()
