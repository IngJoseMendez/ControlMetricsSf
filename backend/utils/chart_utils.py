# -*- coding: utf-8 -*-
"""Utilidad para convertir figuras matplotlib a base64 PNG."""
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def fig_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def new_fig(w=7, h=3.8):
    fig, ax = plt.subplots(figsize=(w, h), facecolor='#FAFAFA')
    ax.set_facecolor('#FAFAFA')
    return fig, ax


def new_fig2(w=14, h=3.8):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(w, h), facecolor='#FAFAFA')
    ax1.set_facecolor('#FAFAFA')
    ax2.set_facecolor('#FAFAFA')
    return fig, ax1, ax2
