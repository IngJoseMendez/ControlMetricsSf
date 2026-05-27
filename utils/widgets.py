# -*- coding: utf-8 -*-
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS, FONTS


class CollapsibleChart(tk.Frame):
    """Contenedor de gráfica matplotlib con cabecera clicable para colapsar/expandir."""

    def __init__(self, parent, title, figsize=(6, 3.5), **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self._expanded = True
        self._build_header(title)
        self._build_chart(figsize)

    def _build_header(self, title):
        hdr = tk.Frame(self, bg=COLORS['primary_light'], cursor='hand2')
        hdr.pack(fill='x')

        self._arrow = tk.Label(
            hdr, text='▼',
            font=FONTS['label_b'],
            bg=COLORS['primary_light'],
            fg=COLORS['text_white'],
            cursor='hand2',
            padx=10, pady=5,
        )
        self._arrow.pack(side='right')

        title_lbl = tk.Label(
            hdr, text=title,
            font=FONTS['label_b'],
            bg=COLORS['primary_light'],
            fg=COLORS['text_white'],
            padx=10, pady=5,
            anchor='w',
        )
        title_lbl.pack(side='left', fill='x', expand=True)

        for widget in (hdr, self._arrow, title_lbl):
            widget.bind('<Button-1>', self.toggle)

    def _build_chart(self, figsize):
        self._body = tk.Frame(self, bg=COLORS['bg'])
        self._body.pack(fill='both', expand=True)

        self.fig = Figure(figsize=figsize, facecolor=COLORS['bg'])
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self._body)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def toggle(self, event=None):
        if self._expanded:
            self._body.pack_forget()
            self._arrow.configure(text='▶')
        else:
            self._body.pack(fill='both', expand=True)
            self._arrow.configure(text='▼')
        self._expanded = not self._expanded

    def draw(self):
        self.canvas.draw()
