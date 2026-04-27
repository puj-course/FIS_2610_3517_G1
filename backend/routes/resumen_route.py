from fastapi import APIRouter, HTTPException
from backend.models import get_connection

router = APIRouter()

@router.get("/resumen/{paciente_id}")
def obtener_resumen(paciente_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Verificar que el paciente existe
        cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        # Medicamentos activos del paciente
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM medicamentos
            WHERE paciente_id = ?
        """, (paciente_id,))
        total_medicamentos = cursor.fetchone()["total"]

        from datetime import date
        hoy = str(date.today())
        # Tomas del día
        cursor.execute("""
            SELECT * FROM tomas
            WHERE paciente_id = ? AND fecha = ?
        """, (paciente_id, hoy))
        tomas_hoy = cursor.fetchall()

        total_tomas_hoy = len(tomas_hoy)
        tomas_registradas = sum(1 for t in tomas_hoy if t["estado"] == "tomado")
    finally:
        conn.close()