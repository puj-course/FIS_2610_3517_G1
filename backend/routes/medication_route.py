#############################################################################
# medication_route.py
# APIRouter: Para crear rutas en FastAPI
# HTTPException: Para devolver errores HTTP
# Se importa la función validar_medicamento de validaciones.py
#############################################################################

from pathlib import Path
import sqlite3
from fastapi import APIRouter, HTTPException
from backend.validaciones import (
    validar_medicamento,
    verificar_paciente_existe,
    verificar_medicamento_duplicado
)

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


@router.post("/")
def registrar_medicamento(data: dict):
    errores = validar_medicamento(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        if not verificar_paciente_existe(int(data["paciente_id"]), conn):
            raise HTTPException(status_code=404, detail="El paciente no existe")

        nombre_medicamento = data["nombre_medicamento"].strip()

        if verificar_medicamento_duplicado(
            nombre_medicamento,
            int(data["paciente_id"]),
            conn
        ):
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

        cursor.execute(
            """
            INSERT INTO medicamentos (
                nombre, dosis, frecuencia, horario,
                fecha_inicio, observaciones, paciente_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre_medicamento,
                dosis,
                frecuencia,
                horario,
                fecha_inicio,
                observaciones,
                int(data["paciente_id"])
            )
        )

        conn.commit()
        return {"mensaje": "Medicamento registrado existosamente"}

    except HTTPException:
        raise

    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar el medicamento: {str(e)}"
        )

    finally:
        conn.close()


@router.get("/paciente/{paciente_id}")
def obtener_medicamentos_paciente(paciente_id: int):
    """
    Devuelve todos los medicamentos de un paciente específico.
    URL: GET /medicamentos/paciente/{paciente_id}
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM medicamentos WHERE paciente_id = ? ORDER BY nombre",
        (paciente_id,)
    )
    meds = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not meds:
        return []

    return meds