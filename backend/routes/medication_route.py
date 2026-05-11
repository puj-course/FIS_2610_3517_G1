# medication_route.py
from fastapi import APIRouter, HTTPException
from backend.validaciones import validar_medicamento
from backend.database import medicamentos_col, pacientes_col
from bson import ObjectId

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])


@router.post("/")
def registrar_medicamento(data: dict):
    errores = validar_medicamento(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    try:
        paciente_id = data["paciente_id"]

        # Verificar paciente existe
        try:
            paciente = pacientes_col.find_one({
                "_id": ObjectId(paciente_id)
            })
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="ID de paciente inválido"
            )

        if not paciente:
            raise HTTPException(
                status_code=404,
                detail="El paciente no existe"
            )

        nombre_medicamento = data["nombre_medicamento"].strip().lower()

        # Verificar duplicado
        duplicado = medicamentos_col.find_one({
            "paciente_id": paciente_id,
            "nombre": nombre_medicamento
        })

        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="El paciente ya tiene registrado este medicamento"
            )

        dosis = f'{data["dosis_cantidad"]} {data["dosis_unidad"]}'
        frecuencia = data["frecuencia"].strip()
        horario = ", ".join(data["horarios"])
        fecha_inicio = data["fecha_inicio"].strip()

        observaciones_extra = (
            f'Concentración: {data["concentracion"]} | '
            f'Forma farmacéutica: {data["forma_farmaceutica"]}'
        )

        observaciones_usuario = data.get("observaciones", "").strip()

        if observaciones_usuario:
            observaciones = f"{observaciones_extra} | {observaciones_usuario}"
        else:
            observaciones = observaciones_extra

        nuevo_medicamento = {
            "nombre": nombre_medicamento,
            "dosis": dosis,
            "frecuencia": frecuencia,
            "horario": horario,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": data.get("fecha_fin", "").strip(),
            "observaciones": observaciones,
            "paciente_id": paciente_id
}

        resultado = medicamentos_col.insert_one(nuevo_medicamento)

        return {
            "mensaje": "Medicamento registrado exitosamente",
            "medicamento_id": str(resultado.inserted_id)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar el medicamento: {str(e)}"
        )


@router.get("/paciente/{paciente_id}")
def obtener_medicamentos_paciente(paciente_id: str):
    try:
        medicamentos = list(
            medicamentos_col.find(
                {"paciente_id": paciente_id}
            ).sort("nombre", 1)
        )

        resultado = []

        for m in medicamentos:
            resultado.append({
                "id": str(m["_id"]),
                "nombre": m.get("nombre", ""),
                "dosis": m.get("dosis", ""),
                "frecuencia": m.get("frecuencia", ""),
                "horario": m.get("horario", ""),
                "fecha_inicio": m.get("fecha_inicio", ""),
                "observaciones": m.get("observaciones", ""),
                "paciente_id": m.get("paciente_id", "")
            })

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener medicamentos: {str(e)}"
        )

from datetime import date as date_type

@router.get("/panel-completo")
def obtener_panel_completo(usuario: Annotated[dict, Depends(obtener_usuario_actual)]):
    from backend.database import tomas_col
    hoy = date_type.today().strftime("%m/%d/%Y")
    hoy_iso = date_type.today().isoformat()
    cuidador_id = usuario.get("id")

    pacientes = list(pacientes_col.find({"cuidador_id": cuidador_id}))
    panel = []

    for p in pacientes:
        paciente_id = str(p["_id"])
        
        # Medicamentos activos hoy
        medicamentos = list(medicamentos_col.find({
            "paciente_id": paciente_id,
            "fecha_inicio": {"$lte": hoy}
        }))
        
        items = []
        for m in medicamentos:
            fecha_fin = m.get("fecha_fin", "")
            if fecha_fin:
                try:
                    from datetime import datetime
                    fin = datetime.strptime(fecha_fin, "%m/%d/%Y").date()
                    if fin < date_type.today():
                        continue
                except:
                    pass
            
            horarios = [h.strip() for h in m.get("horario", "").split(",") if h.strip()]
            med_id = str(m["_id"])
            
            for hora in horarios:
                # Buscar si ya fue tomada
                toma = tomas_col.find_one({
                    "medicamento_id": med_id,
                    "fecha_programada": {"$regex": f"^{hoy_iso}.*{hora}"}
                })
                items.append({
                    "medicamento_id": med_id,
                    "medicamento": m.get("nombre", ""),
                    "dosis": m.get("dosis", ""),
                    "hora": hora,
                    "tomado": toma is not None and toma.get("estado") in ["tomada", "a_tiempo", "tarde"]
                })
        
        if items:
            panel.append({
                "paciente_id": paciente_id,
                "nombres": p.get("nombres", ""),
                "apellidos": p.get("apellidos", ""),
                "medicamentos": items
            })

    return {"panel": panel}