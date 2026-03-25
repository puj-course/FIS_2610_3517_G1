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
from fastapi import APIRouter, HTTPException # Importar la herramienta de FastAPI para agrupar rutas
from backend.validaciones import validar_recordatorio, verificar_medicamento_existe

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

# Endpoint POST recordatoios
@router.post("/")
def crear_recordatorio(data: dict):
    errores = validar_recordatorio(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    conn = sqlite3.connect(DB_PATH)

    try:
        if not verificar_medicamento_existe(int(data["medicamento_id"]), conn):
            raise HTTPException(status_code=404, detail="El medicamento no existe")

        nuevo_id = insertar_recordatorio(data)

        return {
            "mensaje": "Recordatorio creado correctamente",
            "recordatorio_id": nuevo_id
        }

    except HTTPException:
        raise

    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Error interno al crear el recordatorio"
        )

    finally:
        conn.close()
