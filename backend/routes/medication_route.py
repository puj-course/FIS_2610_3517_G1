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
from backend.validaciones import validar_medicamento

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
		cursor.execute(
			"SELECT id FROM pacientes WHERE id = ?", # se usa '?' para no meter el valor directo en el string
			(int(data["paciente_id"]),)
		)
		paciente = cursor.fetchone()

		if not paciente:
			raise HTTPException(status_code=404, detail="El paciente no existe")


		# Insertar medicamento en la tabla
		cursor.execute(
			"""

			INSERT INTO medicamentos (nombre, dosis, frecuencia, horarios, paciente_id)
			VALUES (?, ?, ?, ?, ?)
			""",
			(
				data["nombre"].strip(),
				data["dosis"].strip(),
				data["frecuencia"].strip(),
				data["horarios"].strip(),
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
