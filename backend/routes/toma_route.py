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