# -*- coding: utf-8 -*-
"""FastAPI – ControlMetrics SPC Backend."""
import os
import matplotlib
matplotlib.use('Agg')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import normalidad, cartas_xr, cartas_pnpu, carta_c, capacidad, muestreo, mejora, excel

app = FastAPI(
    title="ControlMetrics SPC API",
    description="Statistical Process Control API",
    version="1.0.0",
)

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(normalidad.router, prefix="/api/normalidad", tags=["Normalidad"])
app.include_router(cartas_xr.router,  prefix="/api/cartas-xr",  tags=["Cartas XR"])
app.include_router(cartas_pnpu.router, prefix="/api/cartas-pnpu", tags=["Cartas PNPU"])
app.include_router(carta_c.router,    prefix="/api/carta-c",    tags=["Carta C"])
app.include_router(capacidad.router,  prefix="/api/capacidad",  tags=["Capacidad"])
app.include_router(muestreo.router,   prefix="/api/muestreo",   tags=["Muestreo"])
app.include_router(mejora.router,     prefix="/api/mejora",     tags=["Mejora"])
app.include_router(excel.router,      prefix="/api/excel",      tags=["Excel"])


@app.get("/")
def root():
    return {"status": "ok", "app": "ControlMetrics SPC API v1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
