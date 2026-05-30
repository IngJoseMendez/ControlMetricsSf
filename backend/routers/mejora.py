# -*- coding: utf-8 -*-
"""Router: Plan de Mejora – Sensibilidad del Sistema de Control."""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils.spc_utils import compute_arl
from utils.chart_utils import fig_to_base64
from config import COLORS

router = APIRouter()


def _power_formula(delta_sigma: float, n: int, k: float = 3.0) -> float:
    d   = abs(float(delta_sigma))
    sqn = np.sqrt(max(n, 1))
    beta = (stats.norm.cdf(k - d * sqn) - stats.norm.cdf(-k - d * sqn))
    return float(1.0 - np.clip(beta, 0.0, 1.0))


def _required_n(delta_sigma: float, target_power: float, k: float = 3.0) -> int:
    if abs(delta_sigma) < 1e-10:
        return 999999
    z1b     = stats.norm.ppf(float(np.clip(target_power, 0.001, 0.9999)))
    n_exact = ((k + z1b) / abs(delta_sigma)) ** 2
    return max(1, int(np.ceil(n_exact)))


class MejoraRequest(BaseModel):
    xbar:         float = 3.2400
    sigma:        float = 0.09865
    n:            int   = 6
    t:            float = 15.0
    ucl:          float = 3.3608
    lcl:          float = 3.1192
    xbar_new:     float = 3.30
    target_power: float = 98.0
    k:            float = 3.0


@router.post("")
def calcular_mejora(req: MejoraRequest):
    if req.sigma <= 0:
        raise HTTPException(400, "σ debe ser mayor que 0.")
    target_pwr = req.target_power / 100.0
    if not (0.01 < target_pwr < 0.9999):
        raise HTTPException(400, "Potencia objetivo debe estar entre 1% y 99.99%.")

    delta       = req.xbar_new - req.xbar
    delta_sigma = delta / req.sigma

    r       = compute_arl(req.ucl, req.lcl, req.xbar, req.sigma, req.n, delta=delta)
    power   = r['poder']
    beta    = r['beta']
    nrl     = r['arl']
    ats_min = nrl * req.t
    ats_h   = ats_min / 60.0
    z_val   = float(stats.norm.ppf(power)) if 0 < power < 1 else (float('inf') if power >= 1 else float('-inf'))

    n_req   = _required_n(delta_sigma, target_pwr, req.k)
    z1b     = float(stats.norm.ppf(target_pwr))
    n_half  = max(1, (req.n + n_req) // 2)
    pwr_half = _power_formula(delta_sigma, n_half, req.k)

    charts = _build_charts(req, delta_sigma, power, target_pwr, nrl, req.n, n_req, n_half)

    return {
        "delta_real":  round(delta, 5),
        "delta_sigma": round(delta_sigma, 4),
        "sensitivity": {
            "power":  round(power * 100, 2),
            "beta":   round(beta * 100, 2),
            "z_val":  round(z_val, 4) if abs(z_val) < 99 else None,
            "nrl":    round(nrl, 2) if nrl < 99999 else None,
            "ats_min": round(ats_min, 1) if ats_min < 999999 else None,
            "ats_h":   round(ats_h, 2) if ats_h < 99999 else None,
        },
        "n_required": {
            "n_req":    n_req,
            "z1b":      round(z1b, 4),
            "pwr_curr": round(power * 100, 2),
            "pwr_half": round(pwr_half * 100, 2),
            "n_half":   n_half,
        },
        "charts": charts,
    }


def _build_charts(req, delta_sigma, power, target_pwr, nrl, n, n_req, n_half) -> dict:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5), facecolor='#FAFAFA')

    d_max   = max(4.0, abs(delta_sigma) * 2.5)
    d_range = np.linspace(0, d_max, 400)
    pwrs_d  = [_power_formula(d, n, req.k) * 100 for d in d_range]

    ax1.set_facecolor('#FAFAFA')
    ax1.plot(d_range, pwrs_d, color=COLORS['primary'], lw=2, label=f'n = {n}')
    ax1.fill_between(d_range, pwrs_d, alpha=0.10, color=COLORS['primary'])
    ax1.axvline(abs(delta_sigma), color=COLORS['danger'], lw=1.5, ls='--',
                label=f'δ = {abs(delta_sigma):.2f}σ  →  {power*100:.1f}%')
    ax1.axhline(target_pwr * 100, color=COLORS['warning'], lw=1.2, ls=':',
                label=f'Objetivo {target_pwr*100:.0f}%')
    ax1.axhline(90, color=COLORS['chart_ucl'], lw=1.0, ls=':', alpha=0.7, label='90%')
    ax1.scatter([abs(delta_sigma)], [power * 100], color=COLORS['danger'], s=55, zorder=5)
    ax1.set_xlabel('Corrimiento δ (unidades de σ)', fontsize=8)
    ax1.set_ylabel('Potencia (%)', fontsize=8)
    ax1.set_title(f'Curva de Potencia – Carta X̄  (n = {n})', fontsize=10, fontweight='bold')
    ax1.set_ylim(-2, 107)
    ax1.tick_params(labelsize=8)
    ax1.legend(fontsize=7, loc='lower right')
    ax1.grid(True, alpha=0.3, ls=':')

    n_max   = max(n_req + max(n_req // 2, 5), n * 3, 20)
    n_range = np.arange(1, n_max + 1)
    pwrs_n  = [_power_formula(delta_sigma, int(ni), req.k) * 100 for ni in n_range]

    ax2.set_facecolor('#FAFAFA')
    ax2.plot(n_range, pwrs_n, color=COLORS['primary'], lw=2)
    ax2.fill_between(n_range, pwrs_n, alpha=0.10, color=COLORS['primary'])
    ax2.axvline(n, color=COLORS['chart_data'], lw=1.5, ls='--',
                label=f'n actual = {n}  →  {power*100:.1f}%')
    ax2.axvline(n_req, color=COLORS['danger'], lw=1.5, ls='--',
                label=f'n req. = {n_req}  →  {target_pwr*100:.0f}%')
    ax2.axhline(target_pwr * 100, color=COLORS['warning'], lw=1.2, ls=':',
                label=f'Objetivo {target_pwr*100:.0f}%')
    ax2.axhline(90, color=COLORS['chart_ucl'], lw=1.0, ls=':', alpha=0.7, label='90%')
    ax2.scatter([n],     [power * 100],         color=COLORS['chart_data'], s=55, zorder=5)
    ax2.scatter([n_req], [target_pwr * 100],     color=COLORS['danger'],    s=55, zorder=5)
    ax2.set_xlabel('Tamaño de subgrupo n', fontsize=8)
    ax2.set_ylabel('Potencia (%)', fontsize=8)
    ax2.set_title(f'Potencia vs n  |  δ = {abs(delta_sigma):.2f}σ', fontsize=10, fontweight='bold')
    ax2.set_ylim(-2, 107)
    ax2.set_xlim(0, n_max + 1)
    ax2.tick_params(labelsize=8)
    ax2.legend(fontsize=7, loc='lower right')
    ax2.grid(True, alpha=0.3, ls=':')

    fig.tight_layout(pad=1.5)
    return {"combined": fig_to_base64(fig)}
