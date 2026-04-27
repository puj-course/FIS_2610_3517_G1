from fastapi import APIRouter, HTTPException
from datetime import date, datetime
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

        # Tomas del día
        hoy = str(date.today())
        cursor.execute("""
            SELECT * FROM tomas
            WHERE paciente_id = ? AND fecha = ?
        """, (paciente_id, hoy))
        tomas_hoy = cursor.fetchall()

        total_tomas_hoy = len(tomas_hoy)
        tomas_registradas = sum(1 for t in tomas_hoy if t["estado"] == "tomado")

        # Tomas atrasadas
        hora_actual = datetime.now()
        tomas_atrasadas = 0
        for t in tomas_hoy:
            if t["estado"] != "tomado":
                try:
                    hora_prog = datetime.strptime(t["hora_programada"], "%H:%M")
                    hora_prog = hora_actual.replace(
                        hour=hora_prog.hour,
                        minute=hora_prog.minute,
                        second=0, microsecond=0
                    )
                    diferencia = (hora_actual - hora_prog).total_seconds() / 60
                    if diferencia > 60:
                        tomas_atrasadas += 1
                except ValueError:
                    pass

        porcentaje = round((tomas_registradas / total_tomas_hoy) * 100, 1) if total_tomas_hoy > 0 else 0

        return {
            "paciente_id": paciente_id,
            "total_medicamentos_activos": total_medicamentos,
            "tomas_registradas_hoy": tomas_registradas,
            "tomas_atrasadas": tomas_atrasadas,
            "total_tomas_esperadas_hoy": total_tomas_hoy,
            "porcentaje_cumplimiento": porcentaje
        }
    finally:
        conn.close()