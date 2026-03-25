#############################################################################
#
#	Ruta para los recordatorios
#	prefix="/recordatorios" Hace que todas las rutas de este archivo, 
#				cuando existan empiecen con /recordatorios.
#	tags=["Recordatorios"]  Sirve para que Swagger /docs agrupe esas rutas
#				bajo el nombre de "Recordatorios"
#
#############################################################################
import sqlite3
from pathlib import Path
from fastapi import APIRouter # Importar la herramienta de FastAPI para agrupar rutas

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"]) # Crea el router de este módulo

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

def insertar_recordatorio(data: dict) -> int:
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()

	try:
		cursor.execute(
			"""
			INSERT INTO recordatorios (
				medicamento_id,
				hora_recordatorio,
				fecha_inicio,
				activo,
				observaciones
			)
			VALUES (?, ?, ?, ?, ?)
			""",
			(
				int(data["medicamento_id"]),
				data["hora_recordatorio"].strip(),
				data["fecha_inicio"].strip(),
				int(data.get("activo", 1)),
				data.get("observaciones", "").strip()
			)
		)
		conn.commit()
		return cursor.lastrowid
	finally:
		conn.close()
