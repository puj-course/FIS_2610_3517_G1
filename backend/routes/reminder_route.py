import sqlite3 
from fastapi import APIRouter, HTTPException
from bson import ObjectId

from backend.database import (
    medicamentos_col,
    recordatorios_col
)

from backend.models import (
    get_recordatorios_por_paciente,
    get_panel_dia_por_paciente
)

from backend.validaciones import validar_recordatorio

try:
    from backend.alertas.bootstrap import publisher
except Exception:
    publisher = None


router = APIRouter(
    prefix="/recordatorios",
    tags=["Recordatorios"]
)


# 🔹 Helper
def obtener_medicamento_por_id(medicamento_id: int):
    return medicamentos_col.find_one({
        "$or": [
            {"id": medicamento_id},
            {"medicamento_id": medicamento_id}
        ]
    })


def obtener_paciente_id_de_medicamento(medicamento: dict):
    return medicamento.get("paciente_id")


# =========================
# POST: crear recordatorio
# =========================
@router.post(
    "/",
    responses={
        400: {"description": "Datos inválidos para crear el recordatorio"},
        404: {"description": "El medicamento asociado no existe"},
        500: {"description": "Error interno al crear el recordatorio"},
    },
)
def crear_recordatorio(data: dict):
    errores = validar_recordatorio(data)

    if errores:
        raise HTTPException(
            status_code=400,
            detail="; ".join(errores)
        )

    try:
        medicamento_id = int(data["medicamento_id"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="medicamento_id debe ser un entero válido"
        )

    medicamento = obtener_medicamento_por_id(medicamento_id)

    if not medicamento:
        raise HTTPException(
            status_code=404,
            detail="El medicamento no existe"
        )

    paciente_id = obtener_paciente_id_de_medicamento(medicamento)

    nuevo_id = ObjectId()

    recordatorio = {
        "_id": nuevo_id,
        "id": str(nuevo_id),
        "medicamento_id": medicamento_id,
        "paciente_id": paciente_id,
        "hora_recordatorio": data["hora_recordatorio"].strip(),
        "fecha_inicio": data["fecha_inicio"].strip(),
        "activo": int(data.get("activo", 1)),
        "observaciones": data.get("observaciones", "").strip(),
        "tomado": False
    }

    try:
        recordatorios_col.insert_one(recordatorio)

        if publisher:
            publisher.notify({
                "type": "reminder_created",
                "recordatorio_id": str(nuevo_id),
                "medicamento_id": medicamento_id,
                "paciente_id": paciente_id,
                "hora_recordatorio": recordatorio["hora_recordatorio"],
                "fecha_inicio": recordatorio["fecha_inicio"],
                "activo": recordatorio["activo"],
                "observaciones": recordatorio["observaciones"]
            })

        return {
            "mensaje": "Recordatorio creado correctamente",
            "recordatorio_id": str(nuevo_id)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el recordatorio: {str(e)}"
        )


# =========================
# GET: panel del día
# =========================
@router.get("/panel-dia")
def obtener_panel_dia():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombres, apellidos FROM pacientes")
        pacientes = cursor.fetchall()

    finally:
        conn.close()

    panel = []

    for p in pacientes:

        filas = get_panel_dia_por_paciente(p["id"])
        medicamentos = []

        for f in filas:
            f = dict(f)

            medicamentos.append({
                "recordatorio_id": f.get("recordatorio_id"),
                "medicamento_id": f.get("medicamento_id"),
                "medicamento": f.get("medicamento_nombre"),
                "dosis": f.get("dosis"),
                "hora": f.get("hora_recordatorio"),
                "tomado": bool(f.get("tomada", 0))
            })

        if medicamentos:
            panel.append({
                "paciente_id": p["id"],
                "nombres": p["nombres"],
                "apellidos": p["apellidos"],
                "medicamentos": medicamentos
            })

    return {"panel": panel}


# =========================
# GET: listar recordatorios
# =========================
@router.get("/{paciente_id}")
def listar_recordatorios(paciente_id: int):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    try:
        filas = get_recordatorios_por_paciente(paciente_id)

        recordatorios = []

        for fila in filas:
            recordatorios.append({
                "id": fila["id"],
                "medicamento_id": fila["medicamento_id"],
                "medicamento_nombre": fila["medicamento_nombre"],
                "dosis": fila["dosis"],
                "hora_recordatorio": fila["hora_recordatorio"],
                "fecha_inicio": fila["fecha_inicio"],
                "activo": fila["activo"],
                "observaciones": fila["observaciones"]
            })

        return {"recordatorios": recordatorios}

    finally:
        conn.close()
