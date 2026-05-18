from __future__ import annotations

from typing import Any

from bson import ObjectId
from fastapi import APIRouter
from pymongo.errors import PyMongoError

from backend.database import (
    medicamentos_col,
    pacientes_col,
    recordatorios_col,
    tomas_col,
)
from backend.quality_metrics import (
    OBJETIVO_LATENCIA_MS,
    construir_reporte_metricas,
)


router = APIRouter(prefix="/metricas-calidad", tags=["Metricas de Calidad"])


def _serializar_documento(valor: Any) -> Any:
    if isinstance(valor, ObjectId):
        return str(valor)

    if isinstance(valor, list):
        return [_serializar_documento(item) for item in valor]

    if isinstance(valor, dict):
        return {
            llave: _serializar_documento(contenido)
            for llave, contenido in valor.items()
        }

    return valor


def _listar_documentos(coleccion) -> list[dict[str, Any]]:
    try:
        return _serializar_documento(list(coleccion.find({})))
    except PyMongoError:
        return []


def _obtener_lista(payload: dict[str, Any], llave: str) -> list[dict[str, Any]]:
    valor = payload.get(llave, [])
    return valor if isinstance(valor, list) else []


def _obtener_objetivo_ms(payload: dict[str, Any] | None = None) -> float:
    if not payload:
        return OBJETIVO_LATENCIA_MS

    try:
        objetivo = float(payload.get("objetivo_ms", OBJETIVO_LATENCIA_MS))
    except (TypeError, ValueError):
        return OBJETIVO_LATENCIA_MS

    return objetivo if objetivo > 0 else OBJETIVO_LATENCIA_MS


@router.get("/resumen")
def obtener_metricas_calidad(incluir_detalle: bool = True):
    pacientes = _listar_documentos(pacientes_col)
    medicamentos = _listar_documentos(medicamentos_col)
    recordatorios = _listar_documentos(recordatorios_col)
    tomas = _listar_documentos(tomas_col)

    return construir_reporte_metricas(
        pacientes=pacientes,
        medicamentos=medicamentos,
        recordatorios=recordatorios,
        tomas=tomas,
        incluir_detalle=incluir_detalle,
    )


@router.post("/evaluar")
def evaluar_metricas_calidad(payload: dict[str, Any], incluir_detalle: bool = True):
    return construir_reporte_metricas(
        pacientes=_obtener_lista(payload, "pacientes"),
        medicamentos=_obtener_lista(payload, "medicamentos"),
        recordatorios=_obtener_lista(payload, "recordatorios"),
        tomas=_obtener_lista(payload, "tomas"),
        objetivo_ms=_obtener_objetivo_ms(payload),
        incluir_detalle=incluir_detalle,
    )
