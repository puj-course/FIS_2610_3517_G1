from fastapi import APIRouter, HTTPException
from backend.models import get_connection

router = APIRouter()

@router.get("/resumen/{paciente_id}")
def obtener_resumen(paciente_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        pass
    finally:
        conn.close()