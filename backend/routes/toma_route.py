from fastapi import APIRouter
from datetime import date
from toma_repository import TomaRepository

router = APIRouter(prefix="/tomas", tags=["Tomas"])

repositorio = TomaRepository()

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


@router.get("/{paciente_id}")
def obtener_tomas(paciente_id: int, fecha: str = None):
    """
    Retorna las tomas del día de un paciente.
    Si no se envía fecha, usa la fecha de hoy.
    """
    if not fecha:
        fecha = str(date.today())
    tomas = repositorio.obtener_tomas_del_dia(paciente_id, fecha)
    return {"tomas": [dict(t) for t in tomas]}