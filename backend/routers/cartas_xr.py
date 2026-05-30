# -*- coding: utf-8 -*-
"""Router: Cartas de Control X̄-R."""
import numpy as np
from scipy.stats import norm
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from utils.spc_utils import (compute_xbar_r, compute_control_limits_xr,
                              detect_out_of_control, western_electric_rules,
                              compute_arl)
from utils.chart_utils import fig_to_base64, new_fig
from config import COLORS, FASE_I_DATA, FASE_II_DATA

router = APIRouter()


class LimitesXR(BaseModel):
    cl_x: float
    ucl_x: float
    lcl_x: float
    cl_r: float
    ucl_r: float
    lcl_r: float
    sigma_est: Optional[float] = None


class CartaXRRequest(BaseModel):
    data: List[List[float]]
    n: int = 6
    limits: Optional[LimitesXR] = None
    lie: Optional[float] = None
    lse: Optional[float] = None
    target: Optional[float] = None


class PowerRequest(BaseModel):
    ucl: float
    lcl: float
    cl: float
    sigma: float
    n: int
    d_min: float = 0.0
    d_max: float = 3.0
    step: float = 0.25


@router.post("")
def calcular_cartas_xr(req: CartaXRRequest):
    if len(req.data) < 2:
        raise HTTPException(400, "Se necesitan al menos 2 subgrupos.")
    n = req.n
    if not (2 <= n <= 10):
        raise HTTPException(400, "n debe estar entre 2 y 10.")

    xbars, ranges = compute_xbar_r(req.data)

    if req.limits:
        lim = {
            'xbar_bar': req.limits.cl_x,
            'cl_x':     req.limits.cl_x,
            'ucl_x':    req.limits.ucl_x,
            'lcl_x':    req.limits.lcl_x,
            'cl_r':     req.limits.cl_r,
            'ucl_r':    req.limits.ucl_r,
            'lcl_r':    req.limits.lcl_r,
            'r_bar':    req.limits.cl_r,
            'sigma_est': req.limits.sigma_est,
        }
    else:
        lim = compute_control_limits_xr(xbars, ranges, n)

    ooc_x = detect_out_of_control(xbars, lim['ucl_x'], lim['lcl_x'])
    ooc_r = detect_out_of_control(ranges, lim['ucl_r'], lim['lcl_r'])
    we_x  = western_electric_rules(xbars, lim['ucl_x'], lim['cl_x'], lim['lcl_x'])
    we_r  = western_electric_rules(ranges, lim['ucl_r'], lim['cl_r'], lim['lcl_r'])

    charts = _build_charts(xbars, ranges, lim, ooc_x, ooc_r, we_x, we_r,
                           req.lie, req.lse, req.target)
    return {
        "xbars":  [round(v, 5) for v in xbars],
        "ranges": [round(v, 5) for v in ranges],
        "limits": {k: round(v, 5) if v is not None else None for k, v in lim.items()},
        "ooc_x":  ooc_x,
        "ooc_r":  ooc_r,
        "we_violations_x": {str(k): v for k, v in we_x.items()},
        "we_violations_r": {str(k): v for k, v in we_r.items()},
        "charts": charts,
    }


@router.post("/power")
def calcular_potencia(req: PowerRequest):
    delta_range = np.arange(req.d_min, req.d_max + req.step * 0.001, req.step)
    delta_range = delta_range[delta_range <= req.d_max + 1e-9][:50]

    results = []
    for d in delta_range:
        r = compute_arl(req.ucl, req.lcl, req.cl, req.sigma, req.n,
                        delta=float(d) * req.sigma)
        results.append({
            "delta_sigma": round(float(d), 3),
            "delta_real":  round(float(d) * req.sigma, 5),
            "poder":       round(r['poder'], 4),
            "beta":        round(r['beta'], 4),
            "arl":         round(r['arl'], 2) if r['arl'] < 99999 else None,
        })

    chart = _build_power_chart(req, results, delta_range)
    return {"results": results, "chart": chart}


@router.get("/demo/fase1")
def demo_fase1():
    return {"data": FASE_I_DATA}


@router.get("/demo/fase2")
def demo_fase2():
    return {"data": FASE_II_DATA}


def _build_charts(xbars, ranges, lim, ooc_x, ooc_r, we_x, we_r,
                  lie, lse, target) -> dict:
    sg = list(range(1, len(xbars) + 1))

    we_pts_x = set()
    we_pts_r = set()
    if we_x:
        for k in range(2, 7):
            we_pts_x |= set(we_x.get(k, []))
        we_pts_x -= set(ooc_x)
    if we_r:
        for k in range(2, 7):
            we_pts_r |= set(we_r.get(k, []))
        we_pts_r -= set(ooc_r)

    import matplotlib.pyplot as plt
    fig, (ax_x, ax_r) = plt.subplots(2, 1, figsize=(11, 7), facecolor='#FAFAFA')

    for ax, values, ucl, cl, lcl, ooc, we_pts, ylabel, title, su, sl, tgt in [
        (ax_x, xbars, lim['ucl_x'], lim['cl_x'], lim['lcl_x'],
         ooc_x, we_pts_x, 'Media X̄ (lb)', 'Carta X̄ – Media del Proceso', lse, lie, target),
        (ax_r, ranges, lim['ucl_r'], lim['cl_r'], lim['lcl_r'],
         ooc_r, we_pts_r, 'Rango R (lb)', 'Carta R – Rango del Proceso', None, None, None),
    ]:
        ax.set_facecolor('#FAFAFA')
        ax.axhline(ucl, color=COLORS['chart_ucl'], lw=1.5, ls='--', label=f'LCS={ucl:.4f}')
        ax.axhline(cl,  color=COLORS['chart_cl'],  lw=1.5, ls='-',  label=f'LC={cl:.4f}')
        ax.axhline(lcl, color=COLORS['chart_lcl'], lw=1.5, ls='--', label=f'LCI={lcl:.4f}')
        if su is not None:
            ax.axhline(su, color=COLORS['chart_spec_u'], lw=1.0, ls=':', label=f'LSE={su}')
        if sl is not None:
            ax.axhline(sl, color=COLORS['chart_spec_l'], lw=1.0, ls=':', label=f'LIE={sl}')
        if tgt is not None:
            ax.axhline(tgt, color=COLORS['chart_target'], lw=1.0, ls='-.', label=f'Obj={tgt}', alpha=0.8)

        ax.plot(sg, values, color=COLORS['chart_data'], lw=1.2, marker='o', markersize=4, zorder=3)
        for idx in ooc:
            ax.plot(sg[idx], values[idx], 'o', color=COLORS['chart_out'], markersize=8, zorder=5)
            ax.annotate(f'SG{sg[idx]}', (sg[idx], values[idx]),
                        textcoords='offset points', xytext=(4, 4), fontsize=7, color=COLORS['chart_out'])
        _we_lbl = False
        for idx in sorted(we_pts):
            if idx < len(sg):
                lbl = 'Regla WE' if not _we_lbl else '_nolegend_'
                ax.plot(sg[idx], values[idx], 'D', color=COLORS['warning'],
                        markersize=7, zorder=4, label=lbl, markeredgecolor='#E65100', markeredgewidth=0.8)
                _we_lbl = True
        ax.set_xlabel('N° de Subgrupo', fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
        ax.set_xlim(0.5, len(sg) + 0.5)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=7, loc='upper right', ncol=2)
        ax.grid(True, alpha=0.3, linestyle=':')

    fig.tight_layout(pad=1.5)
    return {"combined": fig_to_base64(fig)}


def _build_power_chart(req, results, delta_range) -> str:
    deltas_smooth = np.linspace(req.d_min, req.d_max, 300)
    powers_smooth = [
        compute_arl(req.ucl, req.lcl, req.cl, req.sigma, req.n,
                    delta=float(d) * req.sigma)['poder'] * 100
        for d in deltas_smooth
    ]

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 3.5), facecolor='#FAFAFA')
    ax.set_facecolor('#FAFAFA')
    ax.plot(deltas_smooth, powers_smooth, color=COLORS['primary'], lw=2, label='Potencia')
    ax.fill_between(deltas_smooth, powers_smooth, alpha=0.12, color=COLORS['primary'])
    ax.scatter([r['delta_sigma'] for r in results],
               [r['poder'] * 100 for r in results],
               color=COLORS['primary'], s=28, zorder=4)
    ax.axhline(90, color=COLORS['chart_ucl'], lw=1.2, ls='--', label='90%', alpha=0.9)
    ax.axhline(50, color=COLORS['warning'],   lw=1.0, ls=':',  label='50%', alpha=0.8)
    ax.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
    ax.set_ylabel('Potencia (%)', fontsize=8)
    ax.set_title('Curva de Potencia – Carta X̄', fontsize=10, fontweight='bold')
    ax.set_ylim(-2, 107)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc='lower right')
    ax.grid(True, alpha=0.3, linestyle=':')
    fig.tight_layout(pad=1.2)
    return fig_to_base64(fig)
