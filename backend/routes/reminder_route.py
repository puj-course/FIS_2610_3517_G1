from pathlib import Path
import sqlite3
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def verificar_medicamento_existe(medicamento_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM medicamentos WHERE id = ?",
        (medicamento_id,)
    )
    return cursor.fetchone() is not None


def validar_recordatorio(data: dict):
    if not data.get("medicamento_id"):
        return "Favor ingresar el medicamento del recordatorio"

    hora = data.get("hora_recordatorio") or data.get("hora") or data.get("horario")
    if not hora:
        return "Favor ingresar la hora del recordatorio"

    return None


@router.post("/", status_code=status.HTTP_200_OK)
def crear_recordatorio(data: dict):
    error = validar_recordatorio(data)
    if error:
        raise HTTPException(status_code=400, detail=error)

    medicamento_id = data.get("medicamento_id")
    hora_recordatorio = (
        data.get("hora_recordatorio")
        or data.get("hora")
        or data.get("horario")
    )
    fecha_inicio = data.get("fecha_inicio")
    activo = data.get("activo", 1)
    observaciones = data.get("observaciones")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if not verificar_medicamento_existe(medicamento_id, conn):
            raise HTTPException(
                status_code=404,
                detail="El medicamento no existe"
            )

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
                    medicamento_id,
                    hora_recordatorio,
                    fecha_inicio,
                    activo,
                    observaciones
                )
            )
        except sqlite3.OperationalError:
            try:
                cursor.execute(
                    """
                    INSERT INTO recordatorios (
                        medicamento_id,
                        hora,
                        fecha_inicio,
                        activo,
                        observaciones
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        medicamento_id,
                        hora_recordatorio,
                        fecha_inicio,
                        activo,
                        observaciones
                    )
                )
            except sqlite3.OperationalError:
                cursor.execute(
                    """
                    INSERT INTO recordatorios (
                        medicamento_id,
                        horario,
                        fecha_inicio,
                        activo,
                        observaciones
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        medicamento_id,
                        hora_recordatorio,
                        fecha_inicio,
                        activo,
                        observaciones
                    )
                )

        conn.commit()

        return {
            "status": 200,
            "message": "Recordatorio creado exitosamente"
        }

    finally:
        conn.close()


@router.get("/{paciente_id}")
def consultar_recordatorios(paciente_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM pacientes WHERE id = ?",
            (paciente_id,)
        )
        paciente = cursor.fetchone()

        if not paciente:
            return {
                "status": 404,
                "recordatorios": []
            }

        cursor.execute(
            """
            SELECT
                r.*,
                m.nombre AS medicamento_nombre
            FROM recordatorios r
            JOIN medicamentos m ON r.medicamento_id = m.id
            WHERE m.paciente_id = ?
            """,
            (paciente_id,)
        )
        filas = cursor.fetchall()

        resultado = []
        for fila in filas:
            r = dict(fila)
            resultado.append({
                "id": r.get("id"),
                "medicamento_id": r.get("medicamento_id"),
                "medicamento_nombre": r.get("medicamento_nombre"),
                "hora_recordatorio": (
                    r.get("hora_recordatorio")
                    or r.get("hora")
                    or r.get("horario")
                ),
                "fecha_inicio": r.get("fecha_inicio"),
                "activo": r.get("activo", 1),
                "observaciones": r.get("observaciones")
            })

        return {
            "status": 200,
            "recordatorios": resultado
        }

    finally:
        conn.close()