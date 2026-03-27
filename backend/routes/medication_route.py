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


# Crea el grupo de rutas de medicamentos
router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

# Creacion del endpoint POST
# La funcion responde a una peticion POST en la ruta base de medicamentos
@router.post("/")

def registrar_medicamento(data: dict): # La funcion recibe un diccionario con los datos enviados en el body de request
	errores = validar_medicamento(data) # Se llama a la funcion para validar

	if errores:
		# Responde con error 400 (datos invalidos)
		raise HTTPException(status_code=400, detail=errores)

	conn = sqlite3.connect(DB_PATH) # Abrir conexion con la BD
	cursor = conn.cursor()

	try:
		# Verificar que el paciente exista
		if not verificar_paciente_existe(int(data["paciente_id"]), conn):
			raise HTTPException(status_code=404, detail="El paciente no existe")
		# Verificar que no se está insertando un medicamento doble
		if verificar_medicamento_duplicado(
    			data["nombre"].strip(),
    			int(data["paciente_id"]),
    			conn
		):
    			raise HTTPException(
        			status_code=400,
        			detail="El paciente ya tiene registrado este medicamento"
    			)

		# Insertar medicamento en la tabla
		cursor.execute(
			"""

			INSERT INTO medicamentos (nombre, dosis, frecuencia, horario, fecha_inicio, observaciones, paciente_id)
			VALUES (?, ?, ?, ?, ?, ?, ?)
			""",
			(
				data["nombre"].strip(),
				data["dosis"].strip(),
				data["frecuencia"].strip(),
				data["horario"].strip(),
				data["fecha_inicio"].strip(),
				data.get("observaciones", "").strip(),
				int(data["paciente_id"])
			)
		)

		conn.commit() # Confirmar los cambios en la BD (guardar el INSERT que se acaba de hacer)

		return {"mensaje": "Medicamento registrado existosamente"}

	except HTTPException:
		raise

	except sqlite3.Error as e:
		raise HTTPException(
			status_code=500, 
			detail=f"Error al registrar el medicamento: {str(e)}"
		)

	finally:
		conn.close() # cerrar la conexion
# Endpoint para consultar medicamentos de un paciente
@router.get("/{paciente_id}")
def obtener_medicamentos(paciente_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificamos que el paciente existe
    cursor.execute(f"SELECT id FROM pacientes WHERE id = {paciente_id}")
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Consultamos los medicamentos del paciente
    cursor.execute(f"SELECT * FROM medicamentos WHERE paciente_id = {paciente_id}")
    medicamentos = cursor.fetchall()
    conn.close()

    # Convertimos a lista de diccionarios
    resultado = []
    for m in medicamentos:
        resultado.append({
            "id": m[0],
            "nombre": m[1],
            "dosis": m[2],
            "frecuencia": m[3],
            "horario": m[4],
            "fecha_inicio": m[5],
            "observaciones": m[6],
            "paciente_id": m[7]
        })

    return resultado