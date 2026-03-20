# recordatorio_route.py
# Endpoint para consultar los recordatorios activos de un paciente
from fastapi import APIRouter
from backend.models import get_connection
# Creamos el router que agrupa las rutas de recordatorios
router = APIRouter()
@router.get("/recordatorios/{paciente_id}")
def consultar_recordatorios(paciente_id: int):
    pass