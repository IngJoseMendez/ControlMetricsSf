# -*- coding: utf-8 -*-
"""Router: Análisis de Normalidad."""
import numpy as np
from scipy.stats import norm, probplot
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from utils.spc_utils import (normality_tests, summary_stats,
                              durbin_watson, runs_test, acf_lag1)
from utils.chart_utils import fig_to_base64, new_fig2
from config import COLORS, FASE_I_DATA

router = APIRouter()


class NormalidadRequest(BaseModel):
    data: List[float]
    alpha: float = 0.05


@router.post("")
def analizar_normalidad(req: NormalidadRequest):
    if len(req.data) < 3:
        raise HTTPException(400, "Se necesitan al menos 3 valores.")

    data = req.data
    alpha = req.alpha

    stats_res   = summary_stats(data)
    tests_res   = normality_tests(data)
    dw          = durbin_watson(data)
    rt          = runs_test(data)
    acf         = acf_lag1(data)

    charts = _build_charts(data)

    return {
        "stats": stats_res,
        "tests": {
            k: {
                "statistic": v["statistic"],
                "p_value":   v["p_value"],
                "normal":    bool(v["p_value"] > alpha),
            }
            for k, v in tests_res.items()
        },
        "independence": {
            "dw":  dw,
            "runs": rt,
            "acf":  acf,
        },
        "charts": charts,
    }


@router.get("/demo")
def demo_normalidad():
    flat = [v for row in FASE_I_DATA for v in row]
    return {"data": flat}


def _build_charts(data: list) -> dict:
    arr   = np.array(data)
    mu    = arr.mean()
    sigma = arr.std(ddof=1)

    fig, ax1, ax2 = new_fig2(w=13, h=4)

    # ── Histograma ──
    n_bins = max(8, int(np.sqrt(len(arr))))
    ax1.hist(arr, bins=n_bins, density=True, color=COLORS['primary_lighter'],
             edgecolor='white', alpha=0.85, linewidth=0.5)
    x = np.linspace(arr.min() - sigma, arr.max() + sigma, 300)
    ax1.plot(x, norm.pdf(x, mu, sigma), color=COLORS['danger'],
             linewidth=2, label=f'Normal(μ={mu:.3f}, σ={sigma:.4f})')
    ax1.axvline(mu, color=COLORS['chart_cl'], linewidth=1.5,
                linestyle='--', label='Media')
    ax1.set_xlabel('Peso (lb)', fontsize=9)
    ax1.set_ylabel('Densidad', fontsize=9)
    ax1.set_title('Histograma con curva normal', fontsize=10, fontweight='bold')
    ax1.legend(fontsize=8)
    ax1.tick_params(labelsize=8)
    ax1.grid(True, alpha=0.25, linestyle=':')

    # ── Q-Q Plot ──
    (osm, osr), (slope, intercept, r) = probplot(arr, dist='norm')
    ax2.scatter(osm, osr, color=COLORS['chart_data'], s=22, zorder=3)
    fit_line = np.array(osm) * slope + intercept
    ax2.plot(osm, fit_line, color=COLORS['danger'], linewidth=1.5,
             label=f'Línea de referencia (R²={r**2:.4f})')
    ax2.set_xlabel('Cuantiles teóricos', fontsize=9)
    ax2.set_ylabel('Cuantiles observados', fontsize=9)
    ax2.set_title('Gráfico de Probabilidad Normal (Q-Q)', fontsize=10, fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.tick_params(labelsize=8)
    ax2.grid(True, alpha=0.25, linestyle=':')

    fig.tight_layout(pad=1.5)
    return {"combined": fig_to_base64(fig)}
