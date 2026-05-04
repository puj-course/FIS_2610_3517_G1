from datetime import date

from fastapi import APIRouter, HTTPException

from backend.models import get_connection
from backend.services.toma_service import TomaService
from backend.toma_repository import TomaRepository
from backend.decorators.historial import (
    HistorialTomas,
    CumplimientoDecorator,
    AlertasDecorator
)

router = APIRouter(prefix="/tomas", tags=["Tomas"])

repositorio = TomaRepository()
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
    """
    Registra una toma de medicamento usando TomaService.

    Este endpoint acepta el formato nuevo:
    - fecha_programada
    - fecha_hora_toma

    Y también conserva compatibilidad con el formato antiguo:
    - fecha
    - hora_programada
    - hora_tomada
    """

    fecha_programada = datos.get("fecha_programada")
    fecha_hora_toma = datos.get("fecha_hora_toma")

    # Compatibilidad con formato anterior
    if not fecha_programada:
        fecha = datos.get("fecha", str(date.today()))
        hora_programada = datos.get("hora_programada")

        if hora_programada:
            fecha_programada = f"{fecha} {hora_programada}"

    if not fecha_hora_toma:
        fecha = datos.get("fecha", str(date.today()))
        hora_tomada = datos.get("hora_tomada")

        if hora_tomada:
            fecha_hora_toma = f"{fecha} {hora_tomada}"

    try:
        resultado = toma_service.registrar_toma(
            paciente_id=datos.get("paciente_id"),
            medicamento_id=datos.get("medicamento_id"),
            recordatorio_id=datos.get("recordatorio_id"),
            fecha_programada=fecha_programada,
            fecha_hora_toma=fecha_hora_toma,
            estado=datos.get("estado", "tomada"),
            observaciones=datos.get("observaciones")
        )

        return resultado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dia/{paciente_id}")
def obtener_tomas(paciente_id: int, fecha: str = None):
    if not fecha:
        fecha = str(date.today())

    tomas = repositorio.obtener_tomas_del_dia(paciente_id, fecha)

    return {
        "tomas": [dict(t) for t in tomas]
    }


@router.get("/historial/{paciente_id}")
def obtener_historial(paciente_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            h.id,
            h.paciente_id,
            h.medicamento_id,
            m.nombre AS medicamento_nombre,
            m.nombre AS medicamento,
            h.recordatorio_id,
            DATE(h.fecha_programada) AS fecha,
            TIME(h.fecha_programada) AS hora_programada,
            TIME(h.fecha_hora_toma) AS hora_tomada,
            h.fecha_programada,
            h.fecha_hora_toma,
            h.diferencia_minutos,
            h.estado,
            h.observaciones
        FROM historial_tomas h
        INNER JOIN medicamentos m
            ON h.medicamento_id = m.id
        WHERE h.paciente_id = ?
        ORDER BY h.fecha_programada DESC
    """, (paciente_id,))

    filas = cursor.fetchall()
    conn.close()

    historial = [dict(f) for f in filas]

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