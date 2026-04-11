import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
from models import get_connection

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def insertar_recordatorio(data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO recordatorios (
                medicamento_id,
                hora_recordatorio,
                fecha_inicio,
                activo,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                int(data["medicamento_id"]),
                data["hora_recordatorio"].strip(),
                data["fecha_inicio"].strip(),
                int(data.get("activo", 1)),
                data.get("observaciones", "").strip()
            )
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


@router.post("/")
def crear_recordatorio(data: dict):
    errores = validar_recordatorio(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    conn = sqlite3.connect(DB_PATH)

    try:
        if not verificar_medicamento_existe(int(data["medicamento_id"]), conn):
            raise HTTPException(status_code=404, detail="El medicamento no existe")

        nuevo_id = insertar_recordatorio(data)

        return {
            "mensaje": "Recordatorio creado correctamente",
            "recordatorio_id": nuevo_id
        }

    except HTTPException:
        raise

    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Error interno al crear el recordatorio"
        )

    finally:
        conn.close()


@router.get("/{paciente_id}")
def consultar_recordatorios(paciente_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        return {"status": 404, "message": "Paciente no encontrado"}

    query = """
        SELECT
            r.id,
            r.medicamento_id,
            r.hora_recordatorio,
            r.fecha_inicio,
            r.activo,
            r.observaciones,
            m.nombre as medicamento_nombre
        FROM recordatorios r
        JOIN medicamentos m ON r.medicamento_id = m.id
        WHERE m.paciente_id = ? AND r.activo = 1
    """
    cursor.execute(query, (paciente_id,))
    recordatorios = cursor.fetchall()
    conn.close()

    resultado = []
    for r in recordatorios:
        resultado.append({
            "id": r["id"],
            "medicamento_id": r["medicamento_id"],
            "medicamento_nombre": r["medicamento_nombre"],
            "hora_recordatorio": r["hora_recordatorio"],
            "fecha_inicio": r["fecha_inicio"],
            "activo": r["activo"],
            "observaciones": r["observaciones"]
        })

    return {"status": 200, "recordatorios": resultado}
