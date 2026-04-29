from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.models import get_connection

router = APIRouter(prefix="/resumen", tags=["Resumen Paciente"])


@router.get("/resumen/{paciente_id}")
def obtener_resumen(paciente_id: int):

    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 1. Verificar que el paciente existe
        cursor.execute(
            "SELECT id, nombres, apellidos FROM pacientes WHERE id = ?",
            (paciente_id,)
        )
        paciente = cursor.fetchone()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        # 2. Medicamentos activos
        cursor.execute(
            "SELECT COUNT(*) AS total FROM medicamentos WHERE paciente_id = ?",
            (paciente_id,)
        )
        total_medicamentos = cursor.fetchone()["total"]

        # 3. Tomas del día (tabla correcta: tomas_medicamento)
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT estado
            FROM tomas_medicamento
            WHERE paciente_id = ?
              AND fecha_programada LIKE ?
            """,
            (paciente_id, hoy + "%")
        )
        tomas_hoy = cursor.fetchall()

        total_tomas_hoy   = len(tomas_hoy)
        tomas_tomadas     = sum(1 for t in tomas_hoy if t["estado"] == "tomado")
        tomas_atrasadas   = sum(1 for t in tomas_hoy if t["estado"] == "pendiente")
        porcentaje        = (
            round((tomas_tomadas / total_tomas_hoy) * 100, 1)
            if total_tomas_hoy > 0 else 0
        )

        # 4. Alertas activas (no atendidas)
        cursor.execute(
            """
            SELECT id, tipo, mensaje, severidad, fecha_creacion
            FROM alertas
            WHERE paciente_id = ? AND atendida = 0
            ORDER BY fecha_creacion DESC
            LIMIT 10
            """,
            (paciente_id,)
        )
        alertas = [dict(a) for a in cursor.fetchall()]

        return {
            "paciente_id":                 paciente_id,
            "nombre_paciente":             f"{paciente['nombres']} {paciente['apellidos']}",
            "total_medicamentos_activos":  total_medicamentos,
            "tomas_registradas_hoy":       tomas_tomadas,
            "tomas_atrasadas":             tomas_atrasadas,
            "total_tomas_esperadas_hoy":   total_tomas_hoy,
            "porcentaje_cumplimiento":     porcentaje,
            "alertas_activas":             alertas
        }

    finally:
        conn.close()
