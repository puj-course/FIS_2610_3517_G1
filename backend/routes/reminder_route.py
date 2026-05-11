from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from datetime import date as date_type, datetime
from bson import ObjectId

from backend.database import medicamentos_col, recordatorios_col, pacientes_col, tomas_col
from backend.validaciones import validar_recordatorio
from backend.auth import verify_jwt

try:
    from backend.alertas.bootstrap import publisher
except Exception:
    publisher = None

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])
security = HTTPBearer()


def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_jwt(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload


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


@router.post("/")
def crear_recordatorio(data: dict):
    errores = validar_recordatorio(data)
    if errores:
        raise HTTPException(status_code=400, detail="; ".join(errores))

    medicamento_id = str(data["medicamento_id"]).strip()
    medicamento = obtener_medicamento_por_id(medicamento_id)

    if not medicamento:
        raise HTTPException(status_code=404, detail="El medicamento no existe")

    paciente_id = medicamento.get("paciente_id")
    if not paciente_id:
        raise HTTPException(status_code=400, detail="El medicamento no tiene paciente asociado")

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

        return {"mensaje": "Recordatorio creado correctamente", "recordatorio_id": recordatorio_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el recordatorio: {str(e)}")


@router.get("/panel-completo")
def obtener_panel_completo(usuario: Annotated[dict, Depends(obtener_usuario_actual)]):
    hoy = date_type.today()
    hoy_iso = hoy.isoformat()
    fmt = "%m/%d/%Y"
    cuidador_id = usuario.get("id")

    pacientes = list(pacientes_col.find({"cuidador_id": cuidador_id}))
    panel = []

    for p in pacientes:
        paciente_id = str(p["_id"])
        medicamentos = list(medicamentos_col.find({"paciente_id": paciente_id}))

        items = []
        for m in medicamentos:
            try:
                inicio = datetime.strptime(m.get("fecha_inicio", ""), fmt).date()
                if inicio > hoy:
                    continue
            except Exception:
                continue

            fecha_fin_str = m.get("fecha_fin", "")
            if fecha_fin_str:
                try:
                    fin = datetime.strptime(fecha_fin_str, fmt).date()
                    if fin < hoy:
                        continue
                except Exception:
                    pass

            horarios = [h.strip() for h in m.get("horario", "").split(",") if h.strip()]
            med_id = str(m["_id"])

            for hora in horarios:
                toma = tomas_col.find_one({
                    "medicamento_id": med_id,
                    "fecha_programada": {"$regex": f"^{hoy_iso}.*{hora}"}
                })
                tomado = toma is not None and toma.get("estado") in ["tomada", "a_tiempo", "tarde"]
                items.append({
                    "medicamento_id": med_id,
                    "medicamento": m.get("nombre", ""),
                    "dosis": m.get("dosis", ""),
                    "hora": hora,
                    "tomado": tomado
                })

        if items:
            panel.append({
                "paciente_id": paciente_id,
                "nombres": p.get("nombres", ""),
                "apellidos": p.get("apellidos", ""),
                "medicamentos": items
            })

    return {"panel": panel}


@router.get("/panel-dia")
def obtener_panel_dia(usuario: Annotated[dict, Depends(obtener_usuario_actual)]):
    hoy = date_type.today().strftime("%m/%d/%Y")
    cuidador_id = usuario.get("id")

    pacientes = list(pacientes_col.find({"cuidador_id": cuidador_id}))
    panel = []

    for p in pacientes:
        paciente_id = str(p["_id"])
        recordatorios = list(recordatorios_col.find({
            "paciente_id": paciente_id,
            "activo": 1,
            "fecha_inicio": {"$lte": hoy}
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


@router.get("/panel-dia/{paciente_id}")
def obtener_panel_dia_paciente(
    paciente_id: str,
    usuario: Annotated[dict, Depends(obtener_usuario_actual)]
):
    recordatorios = list(recordatorios_col.find({
        "paciente_id": paciente_id,
        "activo": 1
    }))

    resultado = []
    for r in recordatorios:
        medicamento = obtener_medicamento_por_id(r.get("medicamento_id"))
        resultado.append({
            "recordatorio_id": str(r["_id"]),
            "paciente_id": paciente_id,
            "medicamento_id": r.get("medicamento_id"),
            "medicamento_nombre": medicamento.get("nombre", "") if medicamento else "",
            "dosis": medicamento.get("dosis", "") if medicamento else "",
            "hora_recordatorio": r.get("hora_recordatorio", ""),
            "fecha_inicio": r.get("fecha_inicio", ""),
            "tomado": r.get("tomado", False),
            "observaciones": r.get("observaciones", ""),
        })

    return {"recordatorios": resultado}


@router.get("/{paciente_id}")
def listar_recordatorios(paciente_id: str):
    recordatorios = list(recordatorios_col.find({"paciente_id": paciente_id}))
    resultado = []
    for r in recordatorios:
        medicamento = obtener_medicamento_por_id(r.get("medicamento_id"))
        resultado.append(serializar_recordatorio(r, medicamento))
    return {"recordatorios": resultado}

    @router.get("/retrasados/{paciente_id}")
def listar_recordatorios_retrasados(paciente_id: str):
    recordatorios = list(recordatorios_col.find({
        "paciente_id": paciente_id,
        "activo": 1,
        "tomado": False
    }))
    resultado = []
    for r in recordatorios:
        medicamento = obtener_medicamento_por_id(r.get("medicamento_id"))
        resultado.append(serializar_recordatorio(r, medicamento))
    return {"recordatorios_retrasados": resultado}

@router.patch("/{recordatorio_id}/tomado")
def marcar_recordatorio_como_tomado(recordatorio_id: str):
    try:
        filtro = {"_id": ObjectId(recordatorio_id)}
    except Exception:
        raise HTTPException(status_code=400, detail="ID de recordatorio inválido")
    resultado = recordatorios_col.update_one(filtro, {"$set": {"tomado": True}})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    return {"mensaje": "Recordatorio marcado como tomado correctamente", "recordatorio_id": recordatorio_id}