# toma_route.py
from datetime import date

from fastapi import APIRouter, HTTPException

from backend.services.toma_service import TomaService
from backend.decorators.historial import (
    HistorialTomas,
    CumplimientoDecorator,
    AlertasDecorator
)

router = APIRouter(prefix="/tomas", tags=["Tomas"])

toma_service = TomaService()


@router.post(
    "/",
    status_code=201,
    responses={
        400: {"description": "Datos inválidos para registrar la toma"},
        404: {"description": "Paciente, medicamento o recordatorio no encontrado"},
        409: {"description": "Ya existe una toma registrada para ese recordatorio y fecha"},
        500: {"description": "Error interno al registrar la toma"},
    },
)
def registrar_toma(datos: dict):
    fecha_programada = datos.get("fecha_programada")
    fecha_hora_toma = datos.get("fecha_hora_toma")

    if not fecha_programada:
        fecha = datos.get("fecha", str(date.today()))
        hora_programada = datos.get("hora_programada")

        if hora_programada:
            fecha_programada = f"{fecha} {hora_programada}:00" if len(hora_programada) == 5 else f"{fecha} {hora_programada}"

    if not fecha_hora_toma:
        fecha = datos.get("fecha", str(date.today()))
        hora_tomada = datos.get("hora_tomada")

        if hora_tomada:
            fecha_hora_toma = f"{fecha} {hora_tomada}:00" if len(hora_tomada) == 5 else f"{fecha} {hora_tomada}"

    try:
        return toma_service.registrar_toma(
            paciente_id=datos.get("paciente_id"),
            medicamento_id=datos.get("medicamento_id"),
            fecha_programada=fecha_programada,
            fecha_hora_toma=fecha_hora_toma,
            estado=datos.get("estado", "tomada"),
            observaciones=datos.get("observaciones")
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al registrar la toma: {str(e)}"
        )


@router.get("/dia/{paciente_id}")
def obtener_tomas(paciente_id: str, fecha: str = None):
    if not fecha:
        fecha = str(date.today())

    tomas = toma_service.obtener_tomas_del_dia(paciente_id, fecha)

    return {
        "tomas": tomas
    }


@router.get("/historial/{paciente_id}")
def obtener_historial(paciente_id: str):
    historial = toma_service.obtener_historial(paciente_id)

    if not historial:
        return {
            "historial": [],
            "cumplimiento": {
                "total_tomas": 0,
                "tomas_realizadas": 0,
                "porcentaje": 0
            },
            "alertas": []
        }

    historial_base = HistorialTomas(historial)
    historial_decorado = CumplimientoDecorator(historial_base)
    historial_decorado = AlertasDecorator(historial_decorado)

    return historial_decorado.obtener_datos()