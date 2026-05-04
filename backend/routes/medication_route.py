
from fastapi import APIRouter, HTTPException
from backend.validaciones import validar_medicamento
from backend.database import medicamentos_col, pacientes_col

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])


@router.post("/")
def registrar_medicamento(data: dict):
    errores = validar_medicamento(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    try:
        paciente_id = int(data["paciente_id"])

        # Verificar paciente existe
        paciente = pacientes_col.find_one({"id": paciente_id})

        if not paciente:
            raise HTTPException(
                status_code=404,
                detail="El paciente no existe"
            )

        nombre_medicamento = data["nombre_medicamento"].strip()

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

        medicamentos_col.insert_one(nuevo_medicamento)

        return {"mensaje": "Medicamento registrado exitosamente"}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar el medicamento: {str(e)}"
        )


@router.get("/paciente/{paciente_id}")
def obtener_medicamentos_paciente(paciente_id: int):
    try:
        meds = list(
            medicamentos_col.find(
                {"paciente_id": paciente_id},
                {"_id": 0}
            ).sort("nombre", 1)
        )

        return meds

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener medicamentos: {str(e)}"
        )