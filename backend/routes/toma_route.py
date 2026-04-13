from fastapi import APIRouter, HTTPException
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
