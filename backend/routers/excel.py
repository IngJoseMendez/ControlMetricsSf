# -*- coding: utf-8 -*-
"""Router: Carga y descarga de archivos Excel."""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from utils.spc_utils import (
    excel_read_single_col,
    excel_read_subgroups,
    excel_read_defects,
    excel_read_muestreo,
    excel_create_template,
)

router = APIRouter()

# ── helpers ──────────────────────────────────────────────────────────────────

async def _save_tmp(file: UploadFile) -> str:
    ext = '.xlsx' if (file.filename or '').lower().endswith('.xlsx') else '.xls'
    fd, path = tempfile.mkstemp(suffix=ext)
    try:
        content = await file.read()
        os.write(fd, content)
    finally:
        os.close(fd)
    return path


# ── Lectura ───────────────────────────────────────────────────────────────────

@router.post("/normalidad")
async def leer_normalidad(file: UploadFile = File(...)):
    path = await _save_tmp(file)
    try:
        data = excel_read_single_col(path)
        if not data:
            raise HTTPException(400, "No se encontraron valores numéricos en la columna A.")
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {e}")
    finally:
        os.unlink(path)


@router.post("/capacidad")
async def leer_capacidad(file: UploadFile = File(...)):
    path = await _save_tmp(file)
    try:
        data = excel_read_single_col(path)
        if not data:
            raise HTTPException(400, "No se encontraron valores numéricos en la columna A.")
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {e}")
    finally:
        os.unlink(path)


@router.post("/cartas-xr")
async def leer_cartas_xr(file: UploadFile = File(...)):
    path = await _save_tmp(file)
    try:
        data = excel_read_subgroups(path)
        if not data:
            raise HTTPException(400, "No se encontraron subgrupos en el archivo.")
        return {"data": data, "n": len(data[0]) if data else 0}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {e}")
    finally:
        os.unlink(path)


@router.post("/carta-c")
async def leer_carta_c(file: UploadFile = File(...)):
    path = await _save_tmp(file)
    try:
        result = excel_read_defects(path)
        if not result.get('cajas'):
            raise HTTPException(400, "No se encontraron defectos en la Hoja 1 (CartaC).")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {e}")
    finally:
        os.unlink(path)


@router.post("/muestreo")
async def leer_muestreo(file: UploadFile = File(...)):
    path = await _save_tmp(file)
    try:
        params = excel_read_muestreo(path)
        n_lote = params.get('n_lote') or params.get('nlote')
        nac    = params.get('nac')
        if n_lote is None and nac is None:
            raise HTTPException(400, "No se encontraron parámetros reconocidos (n_lote, nac).")
        return {"n_lote": int(n_lote) if n_lote else None, "nac": float(nac) if nac else None}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {e}")
    finally:
        os.unlink(path)


# ── Descarga de plantillas ────────────────────────────────────────────────────

PLANTILLAS = {
    "normalidad":  ("single_col", "Plantilla_Normalidad.xlsx"),
    "capacidad":   ("single_col", "Plantilla_Capacidad.xlsx"),
    "cartas-xr":   ("subgroups",  "Plantilla_CartasXR.xlsx"),
    "carta-c":     ("defects",    "Plantilla_CartaC.xlsx"),
    "muestreo":    ("muestreo",   "Plantilla_Muestreo.xlsx"),
}

@router.get("/plantilla/{modulo}")
def descargar_plantilla(modulo: str):
    if modulo not in PLANTILLAS:
        raise HTTPException(404, f"Plantilla '{modulo}' no existe.")
    tipo, filename = PLANTILLAS[modulo]

    fd, path = tempfile.mkstemp(suffix='.xlsx')
    os.close(fd)
    try:
        excel_create_template(path, tipo)
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            background=None,
        )
    except Exception as e:
        os.unlink(path)
        raise HTTPException(500, f"Error al generar plantilla: {e}")
