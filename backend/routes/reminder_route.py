from fastapi import APIRouter, HTTPException
from backend.models import (
    get_connection,
    insertar_recordatorio,
    get_recordatorios_por_paciente,
    get_panel_dia_por_paciente
)
from backend.validaciones import (
    validar_recordatorio,
    verificar_medicamento_existe
)

try:
    from backend.alertas.bootstrap import publisher
except Exception:
    publisher = None


router = APIRouter(
    prefix="/recordatorios",
    tags=["Recordatorios"]
)


def obtener_paciente_id_de_medicamento(medicamento_id: int, conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT paciente_id FROM medicamentos WHERE id = ?",
        (medicamento_id,)
    )
    fila = cursor.fetchone()
    return fila["paciente_id"] if fila else None


@router.post("/")
def crear_recordatorio(data: dict):

    errores = validar_recordatorio(data)

    if errores:
        detalle = "; ".join(errores) if isinstance(errores, list) else str(errores)
        raise HTTPException(
            status_code=400,
            detail=detalle
        )

    try:
        medicamento_id = int(data["medicamento_id"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="medicamento_id debe ser un entero válido"
        )

    conn = get_connection()

    try:
        if not verificar_medicamento_existe(medicamento_id, conn):
            raise HTTPException(
                status_code=404,
                detail="El medicamento no existe"
            )

        nuevo_id = insertar_recordatorio(
            medicamento_id=medicamento_id,
            hora_recordatorio=data["hora_recordatorio"].strip(),
            fecha_inicio=data["fecha_inicio"].strip(),
            activo=int(data.get("activo", 1)),
            observaciones=data.get("observaciones", "").strip()
        )

        paciente_id = obtener_paciente_id_de_medicamento(
            medicamento_id,
            conn
        )

        if publisher:
            publisher.notify({
                "type": "reminder_created",
                "recordatorio_id": nuevo_id,
                "medicamento_id": medicamento_id,
                "paciente_id": paciente_id,
                "hora_recordatorio": data["hora_recordatorio"].strip(),
                "fecha_inicio": data["fecha_inicio"].strip(),
                "activo": int(data.get("activo", 1)),
                "observaciones": data.get("observaciones", "").strip()
            })

        return {
            "mensaje": "Recordatorio creado correctamente",
            "recordatorio_id": nuevo_id
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {e}"
        )

    finally:
        conn.close()


@router.get("/panel-dia")
def obtener_panel_dia():
    """
    Devuelve medicamentos programados para hoy
    de todos los pacientes.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nombres, apellidos FROM pacientes"
        )

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

    return {
        "panel": panel
    }


@router.get("/{paciente_id}")
def listar_recordatorios(paciente_id: int):

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

        return {
            "recordatorios": recordatorios
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener recordatorios: {e}"
        )