import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.validaciones import validar_recordatorio, verificar_medicamento_existe
from datetime import datetime, timedelta


router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])

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


@router.get("/{paciente_id}")
def consultar_recordatorios(paciente_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        return {"status": 404, "message": "Paciente no encontrado"}

    query = """
        SELECT
            r.id,
            r.medicamento_id,
            r.hora_recordatorio,
            r.fecha_inicio,
            r.activo,
            r.observaciones,
            m.nombre as medicamento_nombre
        FROM recordatorios r
        JOIN medicamentos m ON r.medicamento_id = m.id
        WHERE m.paciente_id = ? AND r.activo = 1
    """
    cursor.execute(query, (paciente_id,))
    recordatorios = cursor.fetchall()
    conn.close()

    resultado = []
    for r in recordatorios:
        resultado.append({
            "id": r["id"],
            "medicamento_id": r["medicamento_id"],
            "medicamento_nombre": r["medicamento_nombre"],
            "hora_recordatorio": r["hora_recordatorio"],
            "fecha_inicio": r["fecha_inicio"],
            "activo": r["activo"],
            "observaciones": r["observaciones"]
        })

    return {"status": 200, "recordatorios": resultado}

@router.get("/retrasados/{paciente_id}")
def obtener_recordatorios_retrasados(paciente_id: int):
    """
    Devuelve los recordatorios que llevan más de una hora
    sin ser marcados como tomados.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Verificamos que el paciente existe
    cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
    if not cursor.fetchone():
        conn.close()
        return {"status": 404, "message": "Paciente no encontrado"}

    # Hora límite: hora actual menos 1 hora
    hora_limite = (datetime.now() - timedelta(hours=1)).strftime("%H:%M")

    # Buscamos recordatorios activos, no tomados, con hora pasada hace más de 1 hora
    query = """
        SELECT
            r.id,
            r.medicamento_id,
            r.hora_recordatorio,
            r.observaciones,
            m.nombre as medicamento_nombre,
            p.nombres as paciente_nombres,
            p.apellidos as paciente_apellidos
        FROM recordatorios r
        JOIN medicamentos m ON r.medicamento_id = m.id
        JOIN pacientes p ON m.paciente_id = p.id
        WHERE m.paciente_id = ?
          AND r.activo = 1
          AND r.tomado = 0
          AND r.hora_recordatorio <= ?
    """
    cursor.execute(query, (paciente_id, hora_limite))
    retrasados = cursor.fetchall()
    conn.close()

    resultado = []
    for r in retrasados:
        resultado.append({
            "id":                 r["id"],
            "medicamento_id":     r["medicamento_id"],
            "medicamento_nombre": r["medicamento_nombre"],
            "hora_recordatorio":  r["hora_recordatorio"],
            "paciente":           f"{r['paciente_nombres']} {r['paciente_apellidos']}",
            "observaciones":      r["observaciones"]
        })

    return {"status": 200, "retrasados": resultado}


@router.patch("/{recordatorio_id}/tomado")
def marcar_como_tomado(recordatorio_id: int):
    """
    Marca un recordatorio como tomado y guarda la hora en que se tomó.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificamos que el recordatorio existe
    cursor.execute("SELECT id FROM recordatorios WHERE id = ?", (recordatorio_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")

    # Guardamos la hora actual
    hora_tomado = datetime.now().strftime("%H:%M")
    cursor.execute("""
        UPDATE recordatorios
        SET tomado = 1, hora_tomado = ?
        WHERE id = ?
    """, (hora_tomado, recordatorio_id))

    conn.commit()
    conn.close()

    return {"mensaje": "Medicamento marcado como tomado", "hora_tomado": hora_tomado}

@router.get("/panel-dia")
def obtener_panel_dia():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Traemos todos los recordatorios activos cruzando
    # con medicamentos y pacientes
    cursor.execute("""
        SELECT 
            p.id as paciente_id,
            p.nombres,
            p.apellidos,
            m.nombre as medicamento,
            m.dosis,
            r.id as recordatorio_id,
            r.hora_recordatorio,
            r.tomado
        FROM recordatorios r
        JOIN medicamentos m ON r.medicamento_id = m.id
        JOIN pacientes p ON m.paciente_id = p.id
        WHERE r.activo = 1
        ORDER BY p.id, r.hora_recordatorio
    """)

    filas = cursor.fetchall()
    conn.close()

    # Agrupamos por paciente
    resultado = {}
    for f in filas:
        clave = f["paciente_id"]
        if clave not in resultado:
            resultado[clave] = {
                "paciente_id": f["paciente_id"],
                "nombres": f["nombres"],
                "apellidos": f["apellidos"],
                "medicamentos": []
            }
        resultado[clave]["medicamentos"].append({
            "recordatorio_id": f["recordatorio_id"],
            "medicamento": f["medicamento"],
            "dosis": f["dosis"],
            "hora": f["hora_recordatorio"],
            "tomado": f["tomado"]
        })

    return {"panel": list(resultado.values())}