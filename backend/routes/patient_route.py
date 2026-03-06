# patient_route.py

from fastapi import APIRouter, HTTPException, status
from backend.models import get_connection
from backend.validaciones import validar_paciente, verificar_duplicado
<<<<<<< HEAD
# .....
=======

# .
>>>>>>> features-Karol
router = APIRouter()

@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def registrar_paciente(data: dict):
    # 1. Validar datos obligatorios y formato
    errores = validar_paciente(data)
    if errores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errores
        )

    conn = get_connection()

    try:
        # 2. Verificar duplicado
        if verificar_duplicado(
            data["numero_documento"],
            data["tipo_documento"],
            conn
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un paciente con ese documento"
            )

        # 3. Guardar en base de datos
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pacientes (
                nombres,
                apellidos,
                fecha_nacimiento,
                genero,
                tipo_documento,
                numero_documento,
                telefono_contacto,
                eps_aseguradora,
                diagnostico_principal,
                alergias_conocidas,
                observaciones_adicionales
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["nombres"],
            data["apellidos"],
            data["fecha_nacimiento"],
            data["genero"],
            data["tipo_documento"],
            data["numero_documento"],
            data["telefono_contacto"],
            data["eps_aseguradora"],
            data["diagnostico_principal"],
            data.get("alergias_conocidas", ""),
            data.get("observaciones_adicionales", "")
        ))

        conn.commit()
        paciente_id = cursor.lastrowid

        return {
            "message": "Paciente registrado exitosamente",
            "paciente_id": paciente_id
        }

    finally:
        conn.close()
