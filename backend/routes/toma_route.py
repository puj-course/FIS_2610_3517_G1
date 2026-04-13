<<<<<<< HEAD
﻿from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.toma_service import TomaService
from backend.commands.regisToma_command import RegisToma_command
from backend.commands.invoker import CommandInvoker

router = APIRouter(prefix="/tomas", tags=["tomas"])


class RegistrarTomaRequest(BaseModel):
    paciente_id: int
    medicamento_id: int
    recordatorio_id: int
    fecha_programada: str
    fecha_hora_toma: str
    estado: str = "tomada"
    observaciones: Optional[str] = None


@router.post("/")
def registrar_toma(data: RegistrarTomaRequest):
    try:
        receiver = TomaService()

        command = RegisToma_command(
            receiver=receiver,
            paciente_id=data.paciente_id,
            medicamento_id=data.medicamento_id,
            recordatorio_id=data.recordatorio_id,
            fecha_programada=data.fecha_programada,
            fecha_hora_toma=data.fecha_hora_toma,
            estado=data.estado,
            observaciones=data.observaciones
        )

        invoker = CommandInvoker()
        invoker.set_command(command)

        resultado = invoker.run()
        return resultado

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
=======
from fastapi import APIRouter
from datetime import date
from backend.models import obtener_historial_tomas
from backend.toma_repository import TomaRepository

router = APIRouter(prefix="/tomas", tags=["Tomas"])

repositorio = TomaRepository()


# 🔹 HU-33 - Registrar toma
@router.post("/", status_code=201)
def registrar_toma(datos: dict):
    """
    Registra una nueva toma de medicamento.
    """
    toma_id = repositorio.registrar_toma(
        medicamento_id=datos.get("medicamento_id"),
        paciente_id=datos.get("paciente_id"),
        fecha=datos.get("fecha", str(date.today())),
        hora_programada=datos.get("hora_programada"),
        hora_tomada=datos.get("hora_tomada"),
        estado=datos.get("estado", "pendiente"),
        observaciones=datos.get("observaciones")
    )
    return {"message": "Toma registrada exitosamente", "toma_id": toma_id}


# 🔹 HU-33 - Obtener tomas del día
@router.get("/{paciente_id}")
def obtener_tomas(paciente_id: int, fecha: str = None):
    """
    Retorna las tomas del día de un paciente.
    """
    if not fecha:
        fecha = str(date.today())
    tomas = repositorio.obtener_tomas_del_dia(paciente_id, fecha)
    return {"tomas": [dict(t) for t in tomas]}


# 🔥 HU-35 - Historial de tomas
@router.get("/historial/{paciente_id}")
def obtener_historial(paciente_id: int):
    tomas = obtener_historial_tomas(paciente_id)

    resultado = []

    for t in tomas:
        resultado.append({
            "id": t["id"],
            "paciente_id": t["paciente_id"],
            "medicamento_id": t["medicamento_id"],
            "medicamento": t["nombre"],
            "fecha": t["fecha"],
            "hora_programada": t["hora_programada"],
            "hora_tomado": t["hora_tomada"],
            "estado": t["estado"]
        })

    return {"historial": resultado}
>>>>>>> 746f323ecd9223321641613fefa868daec13de58
