from fastapi import APIRouter

from backend.database import (
    pacientes_col,
    medicamentos_col,
    recordatorios_col,
    tomas_col,
)
from backend.quality_metrics import (
    calcular_completitud_datos,
    calcular_cumplimiento_reglas_negocio,
    medir_latencia_operacion,
)


router = APIRouter(prefix="/metricas-calidad", tags=["Metricas de Calidad"])


def _listar_documentos(coleccion):
    return list(coleccion.find({}))


def _calcular_metricas(pacientes, medicamentos, recordatorios, tomas):
    completitud = calcular_completitud_datos(
        pacientes=pacientes,
        medicamentos=medicamentos,
        recordatorios=recordatorios,
    )

    reglas_negocio = calcular_cumplimiento_reglas_negocio(
        pacientes=pacientes,
        medicamentos=medicamentos,
        recordatorios=recordatorios,
        tomas=tomas,
    )

    latencia = medir_latencia_operacion(
        lambda: {
            "pacientes": len(pacientes),
            "medicamentos": len(medicamentos),
            "recordatorios": len(recordatorios),
            "tomas": len(tomas),
        }
    )

    return {
        "metricas_propias": {
            "completitud_datos": completitud,
            "cumplimiento_reglas_negocio": reglas_negocio,
            "latencia_rendimiento": latencia,
        }
    }


@router.get("/resumen")
def obtener_metricas_calidad():
    pacientes = _listar_documentos(pacientes_col)
    medicamentos = _listar_documentos(medicamentos_col)
    recordatorios = _listar_documentos(recordatorios_col)
    tomas = _listar_documentos(tomas_col)

    return _calcular_metricas(
        pacientes=pacientes,
        medicamentos=medicamentos,
        recordatorios=recordatorios,
        tomas=tomas,
    )


@router.post("/evaluar")
def evaluar_metricas_calidad(payload: dict):
    pacientes = payload.get("pacientes", [])
    medicamentos = payload.get("medicamentos", [])
    recordatorios = payload.get("recordatorios", [])
    tomas = payload.get("tomas", [])

    return _calcular_metricas(
        pacientes=pacientes,
        medicamentos=medicamentos,
        recordatorios=recordatorios,
        tomas=tomas,
    )