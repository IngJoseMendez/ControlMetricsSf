# -*- coding: utf-8 -*-
"""Router: Análisis de Capacidad del Proceso."""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from utils.spc_utils import compute_capability, summary_stats
from utils.chart_utils import fig_to_base64
from config import COLORS, DEFAULTS, FASE_I_DATA

router = APIRouter()


class CapacidadRequest(BaseModel):
    data: List[float]
    lie: float = DEFAULTS['lie_cliente']
    lse: float = DEFAULTS['lse_cliente']
    target: Optional[float] = DEFAULTS['target']
    sigma: Optional[float] = None


@router.post("")
def calcular_capacidad(req: CapacidadRequest):
    if len(req.data) < 5:
        raise HTTPException(400, "Se necesitan al menos 5 valores.")
    if req.lie >= req.lse:
        raise HTTPException(400, "LIE debe ser menor que LSE.")

    cap = compute_capability(req.data, req.lie, req.lse, req.sigma)
    s   = summary_stats(req.data)

    cpk = cap['cpk']
    if cpk >= 1.67:
        evaluacion = "Proceso excelente (Cpk ≥ 1.67)"
        nivel = "excellent"
    elif cpk >= 1.33:
        evaluacion = "Proceso capaz (Cpk ≥ 1.33)"
        nivel = "capable"
    elif cpk >= 1.00:
        evaluacion = "Proceso marginalmente capaz (1.00 ≤ Cpk < 1.33)"
        nivel = "marginal"
    elif cpk >= 0.67:
        evaluacion = "Proceso no capaz – se requieren mejoras"
        nivel = "incapable"
    else:
        evaluacion = "Proceso muy incapaz – acción urgente"
        nivel = "critical"

    charts = _build_charts(req.data, cap, req.lie, req.lse, req.target)

    return {
        "mu":       round(cap['mu'], 5),
        "sigma":    round(cap['sigma'], 5),
        "n":        s['n'],
        "cp":       round(cap['cp'], 4),
        "cpk":      round(cap['cpk'], 4),
        "cpu":      round(cap['cpu'], 4),
        "cpl":      round(cap['cpl'], 4),
        "pnc_sup":  round(cap['pnc_sup'] * 100, 4),
        "pnc_inf":  round(cap['pnc_inf'] * 100, 4),
        "pnc_total": round(cap['pnc_total'] * 100, 4),
        "sigma_level": round(cap['sigma_level'], 2),
        "evaluacion": evaluacion,
        "nivel":    nivel,
        "charts":   charts,
    }


@router.get("/demo")
def demo_capacidad():
    flat = [v for row in FASE_I_DATA for v in row]
    return {"data": flat, "sigma": 0.09865}


def _build_charts(data, cap, lie, lse, target) -> dict:
    arr   = np.array(data)
    mu    = cap['mu']
    sigma = cap['sigma']

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 4.5), facecolor='#FAFAFA')

    # ── Capacidad ──
    ax.set_facecolor('#FAFAFA')
    x_min = min(arr.min(), lie) - 2 * sigma
    x_max = max(arr.max(), lse) + 2 * sigma
    x = np.linspace(x_min, x_max, 500)
    y = stats.norm.pdf(x, mu, sigma)

    ax.fill_between(x[x < lie], stats.norm.pdf(x[x < lie], mu, sigma),
                    alpha=0.35, color=COLORS['danger'], label='No conf. (LIE)')
    ax.fill_between(x[x > lse], stats.norm.pdf(x[x > lse], mu, sigma),
                    alpha=0.35, color=COLORS['accent'], label='No conf. (LSE)')
    mask = (x >= lie) & (x <= lse)
    ax.fill_between(x[mask], stats.norm.pdf(x[mask], mu, sigma),
                    alpha=0.22, color=COLORS['primary_lighter'], label='Conforme')
    ax.plot(x, y, color=COLORS['primary'], lw=2,
            label=f'Normal(μ={mu:.3f}, σ={sigma:.4f})')
    ax.axvline(lie, color=COLORS['chart_spec_l'], lw=1.8, ls='--', label=f'LIE={lie}')
    ax.axvline(lse, color=COLORS['chart_spec_u'], lw=1.8, ls='--', label=f'LSE={lse}')
    ax.axvline(mu,  color=COLORS['primary'],      lw=1.5, ls='-',  label=f'μ={mu:.3f}')
    if target:
        ax.axvline(target, color=COLORS['chart_target'], lw=1.2, ls='-.', alpha=0.8,
                   label=f'Obj={target}')
    ax.set_xlabel('Peso (lb)', fontsize=9)
    ax.set_ylabel('Densidad', fontsize=9)
    ax.set_title(f'Capacidad  Cp={cap["cp"]:.3f}  Cpk={cap["cpk"]:.3f}',
                 fontsize=10, fontweight='bold')
    ax.legend(fontsize=6.5, loc='upper right')
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.25, linestyle=':')

    # ── PNC ──
    ax2.set_facecolor('#FAFAFA')
    cats = ['Por encima\nde LSE', 'Por debajo\nde LIE', 'Total\nno conforme']
    vals = [cap['pnc_sup'] * 100, cap['pnc_inf'] * 100, cap['pnc_total'] * 100]
    colors = [COLORS['accent'], COLORS['danger'], COLORS['primary_light']]
    bars = ax2.bar(cats, vals, color=colors, edgecolor='white', linewidth=0.8, width=0.5)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 f'{val:.3f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2.set_ylabel('% Productos No Conformes', fontsize=9)
    ax2.set_title('Distribución de No Conformes', fontsize=10, fontweight='bold')
    ax2.tick_params(labelsize=8)
    ax2.grid(True, alpha=0.25, linestyle=':', axis='y')
    ax2.set_ylim(0, max(vals) * 1.35 + 0.5)

    fig.tight_layout(pad=1.5)
    return {"combined": fig_to_base64(fig)}
