#	APIRouter sirve para agrupar rutas de la API
#	HTTPException permite devolver errores HTTP de forma controlada
#	status trae constantes con códigos HTTP como 201 (created), 400 (Bad?request), 409 (conflict
#	get_connection es la funcion que abre la conexión con la base de dato

from fastapi import APIRouter, HTTPException, status
from backend.models import get_connection
from backend.validaciones import validar_paciente, verificar_duplicado

router = APIRouter()  # Creación del router

# Definición del router y FastAPI ejecuta la función registrar_pacientes
@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def registrar_paciente(data: dict):  # El cuerpo de la petición debe llegar como un diccionario de python
    # Se revisan errores llamando a validar_paciente
    errores = validar_paciente(data)
    if errores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errores
        )
    # Abrir conexión a la BD, el objeto ´conn´ representa la conexion activa
    conn = get_connection()

    try:
        if verificar_duplicado(
            data["numero_documento"],
            data["tipo_documento"],
            conn
        ):
            # Si se trata de registrar un paciente ya en la plataforma, mostrar el error
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un paciente con ese documento"
            )
        # cursor es el objeto que realmente ejecutas consultas SQL
        cursor = conn.cursor()

        # Datos del paciente, se crea una nueva fila en la tabla PACIENTE con estos valores
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

        conn.commit()  # Confirmar la transaccion en la BD
        paciente_id = cursor.lastrowid  # lastrowid devuelve el id recién generado
        # Mostramos por pantalla el mensaje de éxito junto con la id del paciente
        return {
            "message": "Paciente registrado exitosamente",
            "paciente_id": paciente_id
        }

    finally:  # finally se ejecuta siempre, haya error o no, es decir, siempre se cierra la conexion al final
        conn.close()


# Endpoint para consultar todos los pacientes
@router.get("/pacientes")
def obtener_pacientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()

    # Convertimos los resultados a lista de diccionarios
    resultado = []
    for p in pacientes:
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
            "observaciones_adicionales": p["observaciones_adicionales"]
        })

    return resultado