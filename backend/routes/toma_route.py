from fastapi import APIRouter
from backend.models import obtener_historial_tomas

toma_router = APIRouter(prefix="/tomas", tags=["Tomas"])


@toma_router.get("/historial/{paciente_id}")
def obtener_historial(paciente_id: int):
    tomas = obtener_historial_tomas(paciente_id)

    resultado = []

    for t in tomas:
        resultado.append({
            "id": t["id"],
            "paciente_id": t["paciente_id"],
            "medicamento_id": t["medicamento_id"],
            "medicamento": t["nombre"],
            "fecha": t["fecha_programada"],
            "hora_programada": t["hora_programada"],
            "hora_tomado": t["hora_tomado"],
            "estado": t["estado"]
        })

    return {"historial": resultado}