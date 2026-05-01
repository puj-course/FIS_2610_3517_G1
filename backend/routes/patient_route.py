# APIRouter sirve para agrupar rutas de la API
# HTTPException permite devolver errores HTTP de forma controlada
# status trae constantes con códigos HTTP
# get_connection es la función que abre la conexión con la base de datos

from fastapi import APIRouter, HTTPException, status
from backend.models import get_connection
from backend.validaciones import validar_paciente, verificar_duplicado
from backend.factories.paciente_factory import PacienteGeneralFactory

router = APIRouter()


@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def registrar_paciente(data: dict):
    errores = validar_paciente(data)
    if errores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errores
        )

    conn = get_connection()

    try:
        if verificar_duplicado(
            data["numero_documento"],
            data["tipo_documento"],
            conn
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un paciente con ese documento"
            )

        fabrica = PacienteGeneralFactory()
        paciente = fabrica.crear(data)

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
        """, paciente.como_tupla())

        conn.commit()
        paciente_id = cursor.lastrowid

        return {
            "message": "Paciente registrado exitosamente",
            "paciente_id": paciente_id
        }

    finally:
        conn.close()


@router.get("/pacientes")
def obtener_pacientes():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.nombres,
                p.apellidos,
                p.fecha_nacimiento,
                p.genero,
                p.tipo_documento,
                p.numero_documento,
                p.telefono_contacto,
                p.eps_aseguradora,
                p.diagnostico_principal,
                p.alergias_conocidas,
                p.observaciones_adicionales,

                COALESCE(SUM(
                    CASE 
                        WHEN LOWER(h.estado) = 'tarde' THEN 1 
                        ELSE 0 
                    END
                ), 0) AS total_tomas_atrasadas,

                COALESCE(SUM(
                    CASE 
                        WHEN LOWER(h.estado) = 'omitida' THEN 1 
                        ELSE 0 
                    END
                ), 0) AS total_tomas_omitidas

            FROM pacientes p
            LEFT JOIN historial_tomas h 
                ON h.paciente_id = p.id
            GROUP BY 
                p.id,
                p.nombres,
                p.apellidos,
                p.fecha_nacimiento,
                p.genero,
                p.tipo_documento,
                p.numero_documento,
                p.telefono_contacto,
                p.eps_aseguradora,
                p.diagnostico_principal,
                p.alergias_conocidas,
                p.observaciones_adicionales
            ORDER BY p.id DESC
        """)

        pacientes = cursor.fetchall()
        resultado = []

        for p in pacientes:
            total_tomas_atrasadas = int(p["total_tomas_atrasadas"])
            total_tomas_omitidas = int(p["total_tomas_omitidas"])

            tiene_tomas_atrasadas = total_tomas_atrasadas > 0
            tiene_tomas_omitidas = total_tomas_omitidas > 0

            if tiene_tomas_atrasadas and tiene_tomas_omitidas:
                alerta_tomas = "mixta"
            elif tiene_tomas_atrasadas:
                alerta_tomas = "atrasada"
            elif tiene_tomas_omitidas:
                alerta_tomas = "omitida"
            else:
                alerta_tomas = None

            resultado.append({
                "id": p["id"],
                "nombres": p["nombres"],
                "apellidos": p["apellidos"],
                "fecha_nacimiento": p["fecha_nacimiento"],
                "genero": p["genero"],
                "tipo_documento": p["tipo_documento"],
                "numero_documento": p["numero_documento"],
                "telefono_contacto": p["telefono_contacto"],
                "eps_aseguradora": p["eps_aseguradora"],
                "diagnostico_principal": p["diagnostico_principal"],
                "alergias_conocidas": p["alergias_conocidas"],
                "observaciones_adicionales": p["observaciones_adicionales"],
                "tiene_tomas_atrasadas": tiene_tomas_atrasadas,
                "tiene_tomas_omitidas": tiene_tomas_omitidas,
                "total_tomas_atrasadas": total_tomas_atrasadas,
                "total_tomas_omitidas": total_tomas_omitidas,
                "alerta_tomas": alerta_tomas
            })

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pacientes: {str(e)}"
        )

    finally:
        conn.close()


@router.get("/pacientes/{paciente_id}")
def obtener_paciente(paciente_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        p = cursor.fetchone()

        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )

        return {
            "id": p["id"],
            "nombres": p["nombres"],
            "apellidos": p["apellidos"],
            "fecha_nacimiento": p["fecha_nacimiento"],
            "genero": p["genero"],
            "tipo_documento": p["tipo_documento"],
            "numero_documento": p["numero_documento"],
            "telefono_contacto": p["telefono_contacto"],
            "eps_aseguradora": p["eps_aseguradora"],
            "diagnostico_principal": p["diagnostico_principal"],
            "alergias_conocidas": p["alergias_conocidas"],
            "observaciones_adicionales": p["observaciones_adicionales"]
        }

    finally:
        conn.close()
