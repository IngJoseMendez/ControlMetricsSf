# -*- coding: utf-8 -*-
"""Router: Plan de Muestreo por Aceptación (MIL-STD-105E)."""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from utils.spc_utils import milstd_plan, milstd_code_letter
from utils.chart_utils import fig_to_base64
from config import COLORS

router = APIRouter()


class MuestreoRequest(BaseModel):
    n_lote: int = 960
    nac: float = 4.0
    use_manual: bool = False
    n_plan: Optional[int] = None
    c_plan: Optional[int] = None


@router.post("")
def calcular_muestreo(req: MuestreoRequest):
    nac = req.nac / 100.0

    if req.use_manual and req.n_plan and req.c_plan is not None:
        n_plan = req.n_plan
        c_plan = req.c_plan
        letter = milstd_code_letter(req.n_lote)
    else:
        letter, (n_plan, c_plan, _) = milstd_plan(req.n_lote)

    re_plan = c_plan + 1
    p_range = np.linspace(0, 0.35, 500)
    pa = stats.binom.cdf(c_plan, n_plan, p_range)

    pa_nac  = float(stats.binom.cdf(c_plan, n_plan, nac))
    pa_2nac = float(stats.binom.cdf(c_plan, n_plan, min(2 * nac, 0.999)))
    pa_0    = float(stats.binom.cdf(c_plan, n_plan, 0.0001))
    alpha_r = 1 - pa_nac
    beta_r  = pa_2nac

    aoq = p_range * pa * (req.n_lote - n_plan) / req.n_lote
    aoq_max   = float(np.max(aoq))
    p_aoq_max = float(p_range[np.argmax(aoq)])

    charts = _build_charts(p_range, pa, aoq, nac, pa_nac, n_plan, c_plan,
                           p_aoq_max, aoq_max, req.n_lote)
    return {
        "letra":      letter,
        "n":          n_plan,
        "ac":         c_plan,
        "re":         re_plan,
        "alpha_risk": round(alpha_r * 100, 2),
        "beta_risk":  round(beta_r * 100, 2),
        "pa_0":       round(pa_0 * 100, 1),
        "pa_nac":     round(pa_nac * 100, 1),
        "pa_2nac":    round(pa_2nac * 100, 1),
        "aoql":       round(aoq_max * 100, 2),
        "p_aoql":     round(p_aoq_max * 100, 2),
        "charts":     charts,
    }


@router.get("/demo")
def demo_muestreo():
    return {"n_lote": 960, "nac": 4.0}


def _build_charts(p_range, pa, aoq, nac, pa_nac, n_plan, c_plan,
                  p_aoq_max, aoq_max, n_lote) -> dict:
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 4.5), facecolor='#FAFAFA')

    # ── Curva OC ──
    ax.set_facecolor('#FAFAFA')
    ax.plot(p_range * 100, pa * 100, color=COLORS['primary'], lw=2.5,
            label=f'OC (n={n_plan}, c={c_plan})')
    ax.plot(nac * 100, pa_nac * 100, 'o', color=COLORS['secondary'], markersize=9, zorder=5,
            label=f'NAC={nac*100:.1f}%  Pa={pa_nac*100:.1f}%')
    ax.axvline(nac * 100, color=COLORS['secondary'], lw=1.2, ls='--', alpha=0.7)
    ax.axhline(pa_nac * 100, color=COLORS['secondary'], lw=1.0, ls=':', alpha=0.7)
    ax.fill_between(p_range * 100, pa * 100, alpha=0.08, color=COLORS['primary_lighter'],
                    label='Zona de aceptación')
    ax.axhline(95, color=COLORS['danger'], lw=0.8, ls=':', alpha=0.5, label='95%')
    ax.axhline(10, color=COLORS['warning'], lw=0.8, ls=':', alpha=0.5, label='10%')
    ax.set_xlabel('Proporción de defectuosos p (%)', fontsize=9)
    ax.set_ylabel('Probabilidad de Aceptación Pa (%)', fontsize=9)
    ax.set_title(f'Curva OC  –  Plan n={n_plan}, Ac={c_plan}', fontsize=10, fontweight='bold')
    ax.set_xlim(0, p_range[-1] * 100)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.tick_params(labelsize=8)

    # ── Curva AOQ ──
    ax2.set_facecolor('#FAFAFA')
    ax2.plot(p_range * 100, aoq * 100, color=COLORS['accent'], lw=2.5, label='AOQ')
    ax2.axvline(p_aoq_max * 100, color=COLORS['danger'], lw=1.2, ls='--',
                label=f'AOQL = {aoq_max*100:.2f}%')
    ax2.plot(p_aoq_max * 100, aoq_max * 100, 'o', color=COLORS['danger'], markersize=8, zorder=5)
    ax2.set_xlabel('Proporción de defectuosos p (%)', fontsize=9)
    ax2.set_ylabel('AOQ (%)', fontsize=9)
    ax2.set_title('Calidad Promedio de Salida (AOQ)', fontsize=10, fontweight='bold')
    ax2.set_xlim(0, p_range[-1] * 100)
    ax2.legend(fontsize=7.5)
    ax2.grid(True, alpha=0.3, linestyle=':')
    ax2.tick_params(labelsize=8)

    fig.tight_layout(pad=1.5)
    return {"combined": fig_to_base64(fig)}
