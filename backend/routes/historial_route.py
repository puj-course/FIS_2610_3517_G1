from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from bson import ObjectId

from backend.database import pacientes_col, medicamentos_col, tomas_col
from backend.historial_toma import HistorialTomaBuilder

router = APIRouter(prefix="/historial", tags=["Historial de tomas"])


class RegistrarTomaRequest(BaseModel):
    paciente_id: Union[int, str]
    medicamento_id: Union[int, str]
    recordatorio_id: Optional[Union[int, str]] = None
    fecha_programada: str
    fecha_hora_toma: Optional[str] = None
    observaciones: Optional[str] = None


def obtener_variantes_id(valor):
    variantes = []

    if valor is None:
        return variantes

    variantes.append(valor)
    variantes.append(str(valor))

    try:
        variantes.append(int(valor))
    except (ValueError, TypeError):
        pass

    if ObjectId.is_valid(str(valor)):
        variantes.append(ObjectId(str(valor)))

    variantes_sin_repetir = []
    for item in variantes:
        if item not in variantes_sin_repetir:
            variantes_sin_repetir.append(item)

    return variantes_sin_repetir


def filtro_por_id(valor):
    variantes = obtener_variantes_id(valor)

    return {
        "$or": (
            [{"_id": item} for item in variantes] +
            [{"id": item} for item in variantes]
        )
    }


def serializar_documento(documento):
    if not documento:
        return None

    resultado = {}

    for clave, valor in documento.items():
        if isinstance(valor, ObjectId):
            resultado[clave] = str(valor)
        else:
            resultado[clave] = valor

    if "_id" in resultado:
        resultado["id"] = resultado.get("id", resultado["_id"])
        del resultado["_id"]

    return resultado


def obtener_nombre_medicamento(medicamento_id):
    medicamento = medicamentos_col.find_one(filtro_por_id(medicamento_id))

    if not medicamento:
        return None

    return medicamento.get("nombre")


@router.post("/", status_code=201)
def registrar_toma_historial(data: RegistrarTomaRequest):
    """
    Registra una toma en el historial usando MongoDB.
    Calcula automáticamente el estado con HistorialTomaBuilder.
    """

    paciente = pacientes_col.find_one(filtro_por_id(data.paciente_id))
    if not paciente:
        raise HTTPException(status_code=404, detail="El paciente no existe")

    medicamento = medicamentos_col.find_one(filtro_por_id(data.medicamento_id))
    if not medicamento:
        raise HTTPException(status_code=404, detail="El medicamento no existe")

    try:
        toma = (
            HistorialTomaBuilder()
            .set_paciente(data.paciente_id)
            .set_medicamento(data.medicamento_id)
            .set_recordatorio(data.recordatorio_id)
            .set_fecha_programada(data.fecha_programada)
            .set_fecha_hora_toma(data.fecha_hora_toma)
            .set_observaciones(data.observaciones)
            .build()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filtro_duplicado = {
        "fecha_programada": toma.fecha_programada
    }

    if toma.recordatorio_id is not None:
        filtro_duplicado["recordatorio_id"] = {
            "$in": obtener_variantes_id(toma.recordatorio_id)
        }
    else:
        filtro_duplicado["paciente_id"] = {
            "$in": obtener_variantes_id(toma.paciente_id)
        }
        filtro_duplicado["medicamento_id"] = {
            "$in": obtener_variantes_id(toma.medicamento_id)
        }

    if tomas_col.find_one(filtro_duplicado):
        raise HTTPException(
            status_code=409,
            detail="Ya existe un registro para ese recordatorio y fecha programada"
        )

    documento = {
        "paciente_id": toma.paciente_id,
        "medicamento_id": toma.medicamento_id,
        "medicamento_nombre": medicamento.get("nombre"),
        "recordatorio_id": toma.recordatorio_id,
        "fecha_programada": toma.fecha_programada,
        "fecha_hora_toma": toma.fecha_hora_toma,
        "diferencia_minutos": toma.diferencia_minutos,
        "estado": toma.estado,
        "observaciones": toma.observaciones
    }

    resultado = tomas_col.insert_one(documento)
    documento["_id"] = resultado.inserted_id

    return {
        "mensaje": "Toma registrada correctamente",
        "id": str(resultado.inserted_id),
        "toma": serializar_documento(documento)
    }


@router.get("/{paciente_id}")
def obtener_historial(paciente_id: str):
    """
    Devuelve el historial completo de tomas de un paciente desde MongoDB.
    """

    paciente = pacientes_col.find_one(filtro_por_id(paciente_id))
    if not paciente:
        raise HTTPException(status_code=404, detail="El paciente no existe")

    filtro_historial = {
        "paciente_id": {
            "$in": obtener_variantes_id(paciente_id)
        }
    }

    documentos = list(
        tomas_col
        .find(filtro_historial)
        .sort("fecha_programada", -1)
    )

    historial = []

    for documento in documentos:
        item = serializar_documento(documento)

        if not item.get("medicamento_nombre"):
            item["medicamento_nombre"] = obtener_nombre_medicamento(
                item.get("medicamento_id")
            )

        historial.append(item)

    total = len(historial)
    a_tiempo = sum(1 for toma in historial if toma.get("estado") == "a_tiempo")
    tarde = sum(1 for toma in historial if toma.get("estado") == "tarde")
    omitidas = sum(1 for toma in historial if toma.get("estado") == "omitida")

    porcentaje = round((a_tiempo + tarde) / total * 100, 1) if total > 0 else 0

    return {
        "historial": historial,
        "resumen": {
            "total": total,
            "a_tiempo": a_tiempo,
            "tarde": tarde,
            "omitidas": omitidas,
            "porcentaje_cumplimiento": porcentaje
        }
    }