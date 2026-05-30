# -*- coding: utf-8 -*-
"""Router: Cartas de Control por Atributos p · np · u."""
import numpy as np
import matplotlib.pyplot as plt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal

from utils.spc_utils import (compute_p_chart, compute_np_chart, compute_u_chart,
                              detect_out_of_control)
from utils.chart_utils import fig_to_base64
from config import COLORS

router = APIRouter()


class CartaPNPURequest(BaseModel):
    chart_type: Literal['p', 'np', 'u']
    counts: List[float]
    sizes: Optional[List[float]] = None
    n_const: Optional[int] = None


@router.post("")
def calcular_carta_pnpu(req: CartaPNPURequest):
    ct = req.chart_type
    counts = req.counts
    if len(counts) < 2:
        raise HTTPException(400, "Se necesitan al menos 2 muestras.")

    if ct == 'p':
        if not req.sizes or len(req.sizes) != len(counts):
            raise HTTPException(400, "Para carta p se requieren tamaños de muestra.")
        res = compute_p_chart(counts, req.sizes)
        values = res['p_values']
        ucl_list = res['ucl_p']
        lcl_list = res['lcl_p']
        cl = res['p_bar']
        ooc = [i for i, (v, u, l) in enumerate(zip(values, ucl_list, lcl_list))
               if v > u or v < l]
        chart = _build_chart_p(values, ucl_list, lcl_list, cl, ooc, req.sizes)
        return {"type": "p", "p_bar": res['p_bar'], "ooc": ooc, "chart": chart}

    elif ct == 'np':
        if not req.n_const or req.n_const <= 0:
            raise HTTPException(400, "Para carta np se requiere n constante.")
        res = compute_np_chart(counts, req.n_const)
        values = res['np_values']
        ooc = detect_out_of_control(values, res['ucl_np'], res['lcl_np'])
        chart = _build_chart_fixed(values, res['ucl_np'], res['cl_np'], res['lcl_np'],
                                   ooc, 'Número no conforme', 'Carta np')
        return {"type": "np", "np_bar": res['np_bar'], "p_bar": res['p_bar'],
                "ucl": res['ucl_np'], "cl": res['cl_np'], "lcl": res['lcl_np'],
                "ooc": ooc, "chart": chart}

    else:  # u
        if not req.sizes or len(req.sizes) != len(counts):
            raise HTTPException(400, "Para carta u se requieren tamaños de muestra.")
        res = compute_u_chart(counts, req.sizes)
        values = res['u_values']
        ucl_list = res['ucl_u']
        lcl_list = res['lcl_u']
        ooc = [i for i, (v, u, l) in enumerate(zip(values, ucl_list, lcl_list))
               if v > u or v < l]
        chart = _build_chart_p(values, ucl_list, lcl_list, res['u_bar'], ooc,
                               req.sizes, ylabel='Defectos por unidad (u)',
                               title='Carta u – Defectos por Unidad')
        return {"type": "u", "u_bar": res['u_bar'], "ooc": ooc, "chart": chart}


def _build_chart_p(values, ucl_list, lcl_list, cl, ooc, sizes,
                   ylabel='Proporción no conforme (p)',
                   title='Carta p – Proporción No Conforme') -> str:
    sg = list(range(1, len(values) + 1))
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#FAFAFA')
    ax.set_facecolor('#FAFAFA')

    ax.plot(sg, ucl_list, color=COLORS['chart_ucl'], lw=1.2, ls='--', label='LCS')
    ax.plot(sg, lcl_list, color=COLORS['chart_lcl'], lw=1.2, ls='--', label='LCI')
    ax.axhline(cl, color=COLORS['chart_cl'], lw=1.5, ls='-', label=f'LC={cl:.4f}')
    ax.fill_between(sg, ucl_list, lcl_list, alpha=0.06, color=COLORS['primary'])

    ax.plot(sg, values, color=COLORS['chart_data'], lw=1.2, marker='o', markersize=4, zorder=3)
    for idx in ooc:
        ax.plot(sg[idx], values[idx], 'o', color=COLORS['chart_out'],
                markersize=8, zorder=5)
        ax.annotate(f'M{sg[idx]}', (sg[idx], values[idx]),
                    textcoords='offset points', xytext=(4, 4),
                    fontsize=7, color=COLORS['chart_out'])

    ax.set_xlabel('Número de Muestra', fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
    ax.set_xlim(0.5, len(sg) + 0.5)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle=':')
    fig.tight_layout(pad=1.5)
    return fig_to_base64(fig)


def _build_chart_fixed(values, ucl, cl, lcl, ooc, ylabel, title) -> str:
    sg = list(range(1, len(values) + 1))
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#FAFAFA')
    ax.set_facecolor('#FAFAFA')
    ax.axhline(ucl, color=COLORS['chart_ucl'], lw=1.5, ls='--', label=f'LCS={ucl:.3f}')
    ax.axhline(cl,  color=COLORS['chart_cl'],  lw=1.5, ls='-',  label=f'LC={cl:.3f}')
    ax.axhline(lcl, color=COLORS['chart_lcl'], lw=1.5, ls='--', label=f'LCI={lcl:.3f}')
    ax.plot(sg, values, color=COLORS['chart_data'], lw=1.2, marker='o', markersize=4, zorder=3)
    for idx in ooc:
        ax.plot(sg[idx], values[idx], 'o', color=COLORS['chart_out'],
                markersize=8, zorder=5)
        ax.annotate(f'M{sg[idx]}', (sg[idx], values[idx]),
                    textcoords='offset points', xytext=(4, 4),
                    fontsize=7, color=COLORS['chart_out'])
    ax.set_xlabel('Número de Muestra', fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
    ax.set_xlim(0.5, len(sg) + 0.5)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle=':')
    fig.tight_layout(pad=1.5)
    return fig_to_base64(fig)
