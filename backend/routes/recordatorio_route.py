# recordatorio_route.py
# Endpoint para consultar los recordatorios activos de un paciente

from fastapi import APIRouter
from backend.models import get_connection
from backend.routes.reminder_route import router
# Creamos el router que agrupa las rutas de recordatorios
router = APIRouter()

@router.get("/recordatorios/{paciente_id}")
def consultar_recordatorios(paciente_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    # Primero verificamos que el paciente existe
    cursor.execute(f"SELECT id FROM pacientes WHERE id = {paciente_id}")
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        return {"status": 404, "message": "Paciente no encontrado"}

    # Consulta los recordatorios activos del paciente haciendo JOIN con medicamentos
    # porque recordatorios no tiene paciente_id directo sino medicamento_id
    query = f"""
        SELECT r.id, r.medicamento_id, r.hora, r.dias, r.activo, m.nombre as medicamento_nombre
        FROM recordatorios r
        JOIN medicamentos m ON r.medicamento_id = m.id
        WHERE m.paciente_id = {paciente_id} AND r.activo = 1
    """
    cursor.execute(query)
    recordatorios = cursor.fetchall()
    conn.close()

    # Si no hay recordatorios retorna lista vacía
    resultado = []
    for r in recordatorios:
        resultado.append({
            "id": r["id"],
            "medicamento_id": r["medicamento_id"],
            "medicamento_nombre": r["medicamento_nombre"],
            "hora": r["hora"],
            "dias": r["dias"],
            "activo": r["activo"]
        })

    return {"status": 200, "recordatorios": resultado}