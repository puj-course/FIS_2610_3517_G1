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