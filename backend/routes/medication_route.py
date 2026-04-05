#############################################################################
#	medication_route.py
#	APIRouter: Para crear rutas en FastAPI
#	HTTPException: Para devolver errores HTTP
#	Se importa la cuncion validar_medicamento de validaciones.py
#
#############################################################################

from pathlib import Path
import sqlite3 # Para conectarse a la BD SQLite
from fastapi import APIRouter, HTTPException
from backend.validaciones import validar_medicamento, verificar_paciente_existe, verificar_medicamento_duplicado

# Relacionado al patron observer
from backend.alertas.bootstrap import publisher


# Crea el grupo de rutas de medicamentos
router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"



def limpiar_texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()

# Creacion del endpoint POST
# La funcion responde a una peticion POST en la ruta base de medicamentos
@router.post("/")
def registrar_medicamento(data: dict):
    errores = validar_medicamento(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        paciente_id = int(data["paciente_id"])
        nombre = data["nombre_medicamento"].strip()
        dosis_cantidad = float(data["dosis_cantidad"])
        dosis_unidad = data["dosis_unidad"].strip()
        dosis = f"{dosis_cantidad} {dosis_unidad}"
        horario = ", ".join([h.strip() for h in data.get("horarios", []) if str(h).strip()])
        dias = ", ".join(data.get("dias", [])) if isinstance(data.get("dias", []), list) else ""

        if not verificar_paciente_existe(paciente_id, conn):
            raise HTTPException(status_code=404, detail="El paciente no existe")

        if verificar_medicamento_duplicado(nombre, paciente_id, conn):
            raise HTTPException(
                status_code=400,
                detail="El paciente ya tiene registrado este medicamento"
            )
        
        # Se limpian y preparan los datos para la inserción
        nombre = limpiar_texto(data.get("nombre_medicamento"))
        concentracion = limpiar_texto(data.get("concentracion"))
        forma_farmaceutica = limpiar_texto(data.get("forma_farmaceutica"))
        frecuencia = limpiar_texto(data.get("frecuencia"))
        relacion_comida = limpiar_texto(data.get("relacion_comida"))
        fecha_inicio = limpiar_texto(data.get("fecha_inicio"))
        fecha_fin = limpiar_texto(data.get("fecha_fin")) or None
        via_administracion = limpiar_texto(data.get("via_administracion"))
        medico_receto = limpiar_texto(data.get("medico_receto"))
        instrucciones = limpiar_texto(data.get("instrucciones"))
        observaciones = limpiar_texto(data.get("observaciones"))

        dosis_cantidad = float(data["dosis_cantidad"])
        dosis_unidad = limpiar_texto(data.get("dosis_unidad"))
        dosis = f"{dosis_cantidad} {dosis_unidad}"

        horario = ", ".join([limpiar_texto(h) for h in data.get("horarios", []) if limpiar_texto(h)])
        dias = ", ".join([limpiar_texto(d) for d in data.get("dias", []) if limpiar_texto(d)])

        paciente_id = int(data["paciente_id"])
    
        cursor.execute(
            """
            INSERT INTO medicamentos (
                nombre,
                concentracion,
                forma_farmaceutica,
                dosis,
                dosis_cantidad,
                dosis_unidad,
                frecuencia,
                relacion_comida,
                horario,
                dias,
                fecha_inicio,
                fecha_fin,
                via_administracion,
                medico_receto,
                instrucciones,
                observaciones,
                paciente_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre,
                concentracion,
                forma_farmaceutica,
                dosis,
                dosis_cantidad,
                dosis_unidad,
                frecuencia,
                relacion_comida,
                horario,
                dias,
                fecha_inicio,
                fecha_fin,
                via_administracion,
                medico_receto,
                instrucciones,
                observaciones,
                paciente_id
            )
        )
		nuevo_medicamento_id = cursor.lastrowid
        conn.commit()

		# Para Observer
		publisher.notify({
    		"type": "medication_registered",
    		"medicamento_id": nuevo_medicamento_id,
    		"paciente_id": paciente_id,
    		"nombre": nombre,
    		"dosis": dosis,
    		"frecuencia": frecuencia,
    		"horario": horario,
    		"dias": dias,
    		"fecha_inicio": fecha_inicio
		})

        return {
			"mensaje": "Medicamento registrado exitosamente"
			"medicamento_id": nuevo_medicamento_id
		}

    except HTTPException:
        raise

    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar el medicamento: {str(e)}"
        )

    finally:
        conn.close()
# Endpoint para consultar medicamentos de un paciente
@router.get("/{paciente_id}")
def obtener_medicamentos(paciente_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    cursor.execute("""
        SELECT
            id, nombre, concentracion, forma_farmaceutica, dosis, dosis_cantidad,
            dosis_unidad, frecuencia, relacion_comida, horario, dias, fecha_inicio,
            fecha_fin, via_administracion, medico_receto, instrucciones, observaciones, paciente_id
        FROM medicamentos
        WHERE paciente_id = ?
    """, (paciente_id,))

    medicamentos = cursor.fetchall()
    conn.close()

    resultado = []
    for m in medicamentos:
        resultado.append({
            "id": m[0],
            "nombre": m[1],
            "concentracion": m[2],
            "forma_farmaceutica": m[3],
            "dosis": m[4],
            "dosis_cantidad": m[5],
            "dosis_unidad": m[6],
            "frecuencia": m[7],
            "relacion_comida": m[8],
            "horario": m[9],
            "dias": m[10],
            "fecha_inicio": m[11],
            "fecha_fin": m[12],
            "via_administracion": m[13],
            "medico_receto": m[14],
            "instrucciones": m[15],
            "observaciones": m[16],
            "paciente_id": m[17]
        })

    return resultado
