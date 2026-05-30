# -*- coding: utf-8 -*-
"""Router: Carta C + Diagrama de Pareto."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from utils.spc_utils import compute_control_limits_c, detect_out_of_control
from utils.chart_utils import fig_to_base64
from config import COLORS, CARTA_C_DATA, DEFECTOS_DATA

router = APIRouter()


class CartaCRequest(BaseModel):
    defects: List[int]
    tipos: Optional[Dict[str, int]] = None
    acept: int = 2


@router.post("")
def calcular_carta_c(req: CartaCRequest):
    if len(req.defects) < 2:
        raise HTTPException(400, "Se necesitan al menos 2 cajas.")

    lim  = compute_control_limits_c(req.defects)
    ooc  = detect_out_of_control(req.defects, lim['ucl'], lim['lcl'])
    nc   = sum(1 for d in req.defects if d > req.acept)
    conformidad = [d <= req.acept for d in req.defects]
    chart = _build_charts(req.defects, lim, ooc, req.tipos or {}, req.acept)

    return {
        "c_bar":    round(lim['c_bar'], 4),
        "ucl":      round(lim['ucl'], 4),
        "lcl":      round(lim['lcl'], 4),
        "n_cajas":  len(req.defects),
        "nc_cajas": nc,
        "nc_pct":   round(nc / len(req.defects) * 100, 1),
        "ooc":      ooc,
        "conformidad": conformidad,
        "charts":   chart,
    }


@router.get("/demo")
def demo_carta_c():
    return {"defects": CARTA_C_DATA, "tipos": DEFECTOS_DATA}


def _build_charts(defects, lim, ooc, tipos, acept) -> dict:
    cajas = list(range(1, len(defects) + 1))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 4.5), facecolor='#FAFAFA')

    # ── Carta C ──
    ax.set_facecolor('#FAFAFA')
    ax.axhline(lim['ucl'],   color=COLORS['chart_ucl'], lw=1.5, ls='--', label=f"LCS={lim['ucl']:.3f}")
    ax.axhline(lim['c_bar'], color=COLORS['chart_cl'],  lw=1.5, ls='-',  label=f"C̄={lim['c_bar']:.3f}")
    ax.axhline(lim['lcl'],   color=COLORS['chart_lcl'], lw=1.5, ls='--', label=f"LCI={lim['lcl']:.3f}")
    ax.axhline(acept, color=COLORS['accent'], lw=1.2, ls=':', label=f'Criterio={acept}', alpha=0.8)
    ax.plot(cajas, defects, color=COLORS['chart_data'], lw=1.2, marker='o', markersize=5, zorder=3)
    for idx in ooc:
        ax.plot(cajas[idx], defects[idx], 'o', color=COLORS['chart_out'], markersize=9, zorder=4)
        ax.annotate(f'C{cajas[idx]}', (cajas[idx], defects[idx]),
                    textcoords='offset points', xytext=(4, 4), fontsize=7, color=COLORS['chart_out'])
    ax.set_xlabel('Número de Caja', fontsize=9)
    ax.set_ylabel('Defectos leves', fontsize=9)
    ax.set_title('Carta C – Defectos por Caja', fontsize=10, fontweight='bold')
    ax.set_xlim(0.5, len(cajas) + 0.5)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.tick_params(labelsize=8)

    # ── Pareto ──
    ax2.set_facecolor('#FAFAFA')
    if tipos:
        sorted_t   = sorted(tipos.items(), key=lambda x: x[1], reverse=True)
        names      = [t[0] for t in sorted_t]
        freqs      = [t[1] for t in sorted_t]
        total      = sum(freqs)
        cumulative = np.cumsum(freqs) / total * 100

        bars = ax2.bar(range(len(names)), freqs, color=COLORS['primary_lighter'],
                       edgecolor='white', linewidth=0.8)
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=35, ha='right', fontsize=7)

        ax3 = ax2.twinx()
        ax3.plot(range(len(names)), cumulative, 'o-', color=COLORS['danger'], lw=1.5, markersize=5)
        ax3.axhline(80, color=COLORS['accent'], lw=1.0, ls='--', alpha=0.7, label='80%')
        ax3.set_ylim(0, 115)
        ax3.set_ylabel('% Acumulado', fontsize=8)
        ax3.tick_params(labelsize=7)
        ax3.legend(fontsize=7, loc='lower right')

        for bar, val in zip(bars, freqs):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                     str(val), ha='center', va='bottom', fontsize=7, fontweight='bold')
        ax2.set_ylabel('Frecuencia', fontsize=8)
        ax2.tick_params(labelsize=8)
    else:
        ax2.text(0.5, 0.5, 'Sin datos de tipos de defecto',
                 ha='center', va='center', transform=ax2.transAxes,
                 color=COLORS['text_light'], fontsize=9)

    ax2.set_title('Diagrama de Pareto – Tipos de Defecto', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle=':', axis='y')

    fig.tight_layout(pad=1.5)
    return {"combined": fig_to_base64(fig)}
