# reminder_route.py
from fastapi import APIRouter, HTTPException
from bson import ObjectId

from backend.database import (
    medicamentos_col,
    recordatorios_col,
    pacientes_col
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


def serializar_recordatorio(recordatorio: dict, medicamento: dict = None) -> dict:
    return {
        "id": str(recordatorio.get("_id")),
        "medicamento_id": recordatorio.get("medicamento_id"),
        "paciente_id": recordatorio.get("paciente_id"),
        "medicamento_nombre": medicamento.get("nombre", "") if medicamento else recordatorio.get("medicamento_nombre", ""),
        "dosis": medicamento.get("dosis", "") if medicamento else recordatorio.get("dosis", ""),
        "hora_recordatorio": recordatorio.get("hora_recordatorio", ""),
        "fecha_inicio": recordatorio.get("fecha_inicio", ""),
        "activo": recordatorio.get("activo", 1),
        "observaciones": recordatorio.get("observaciones", ""),
        "tomado": recordatorio.get("tomado", False)
    }


def obtener_medicamento_por_id(medicamento_id: str):
    try:
        return medicamentos_col.find_one({"_id": ObjectId(medicamento_id)})
    except Exception:
        return None


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

    medicamento_id = str(data["medicamento_id"]).strip()

    medicamento = obtener_medicamento_por_id(medicamento_id)

    if not medicamento:
        raise HTTPException(
            status_code=404,
            detail="El medicamento no existe"
        )

    paciente_id = medicamento.get("paciente_id")

    if not paciente_id:
        raise HTTPException(
            status_code=400,
            detail="El medicamento no tiene paciente asociado"
        )

    nuevo_recordatorio = {
        "medicamento_id": medicamento_id,
        "paciente_id": paciente_id,
        "hora_recordatorio": data["hora_recordatorio"].strip(),
        "fecha_inicio": data["fecha_inicio"].strip(),
        "activo": int(data.get("activo", 1)),
        "observaciones": data.get("observaciones", "").strip(),
        "tomado": False
    }

    try:
        resultado = recordatorios_col.insert_one(nuevo_recordatorio)
        recordatorio_id = str(resultado.inserted_id)

        if publisher:
            try:
                publisher.notify({
                    "type": "reminder_created",
                    "recordatorio_id": recordatorio_id,
                    "medicamento_id": medicamento_id,
                    "paciente_id": paciente_id,
                    "hora_recordatorio": nuevo_recordatorio["hora_recordatorio"],
                    "fecha_inicio": nuevo_recordatorio["fecha_inicio"],
                    "activo": nuevo_recordatorio["activo"],
                    "observaciones": nuevo_recordatorio["observaciones"]
                })
            except Exception:
                pass

        return {
            "mensaje": "Recordatorio creado correctamente",
            "recordatorio_id": recordatorio_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el recordatorio: {str(e)}"
        )


@router.get("/panel-dia")
def obtener_panel_dia():
    pacientes = list(pacientes_col.find())
    panel = []

    for p in pacientes:
        paciente_id = str(p["_id"])

        recordatorios = list(recordatorios_col.find({
            "paciente_id": paciente_id,
            "activo": 1
        }))

        medicamentos = []

        for r in recordatorios:
            medicamento = obtener_medicamento_por_id(r.get("medicamento_id"))

            medicamentos.append({
                "recordatorio_id": str(r["_id"]),
                "medicamento_id": r.get("medicamento_id"),
                "medicamento": medicamento.get("nombre", "") if medicamento else "",
                "dosis": medicamento.get("dosis", "") if medicamento else "",
                "hora": r.get("hora_recordatorio", ""),
                "tomado": r.get("tomado", False)
            })

        if medicamentos:
            panel.append({
                "paciente_id": paciente_id,
                "nombres": p.get("nombres", ""),
                "apellidos": p.get("apellidos", ""),
                "medicamentos": medicamentos
            })

    return {"panel": panel}


@router.get("/{paciente_id}")
def listar_recordatorios(paciente_id: str):
    recordatorios = list(recordatorios_col.find({
        "paciente_id": paciente_id
    }))

    resultado = []

    for r in recordatorios:
        medicamento = obtener_medicamento_por_id(r.get("medicamento_id"))
        resultado.append(serializar_recordatorio(r, medicamento))

    return {"recordatorios": resultado}