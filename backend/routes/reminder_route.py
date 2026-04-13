<<<<<<< HEAD
﻿from fastapi import APIRouter, HTTPException
from backend.models import (
    get_connection,
    insertar_recordatorio,
    get_recordatorios_por_paciente,
    get_panel_dia_por_paciente
)
from backend.validaciones import validar_recordatorio
=======
import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.validaciones import validar_recordatorio, verificar_medicamento_existe
from datetime import datetime, timedelta

>>>>>>> 746f323ecd9223321641613fefa868daec13de58

# Para Observer
try:
    from backend.alertas.bootstrap import publisher
except Exception:
    publisher = None

router = APIRouter(
    prefix="/recordatorios",
    tags=["Recordatorios"]
)


def verificar_medicamento_existe(medicamento_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM medicamentos WHERE id = ?",
        (medicamento_id,)
    )
    return cursor.fetchone() is not None


def obtener_paciente_id_de_medicamento(medicamento_id: int, conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT paciente_id FROM medicamentos WHERE id = ?",
        (medicamento_id,)
    )
    fila = cursor.fetchone()
    return fila["paciente_id"] if fila else None


@router.post("/")
def crear_recordatorio(data: dict):
    errores = validar_recordatorio(data)

    if errores:
        detalle = "; ".join(errores) if isinstance(errores, list) else str(errores)
        raise HTTPException(status_code=400, detail=detalle)

    conn = get_connection()

    try:
        medicamento_id = int(data["medicamento_id"])

        if not verificar_medicamento_existe(medicamento_id, conn):
            raise HTTPException(status_code=404, detail="El medicamento no existe")

        nuevo_id = insertar_recordatorio(
            medicamento_id=medicamento_id,
            hora_recordatorio=data["hora_recordatorio"].strip(),
            fecha_inicio=data["fecha_inicio"].strip(),
            activo=int(data.get("activo", 1)),
            observaciones=data.get("observaciones", "").strip()
        )

        paciente_id = obtener_paciente_id_de_medicamento(medicamento_id, conn)

        print("publisher cargado:", publisher, flush=True)

        if publisher:
            print("Voy a publicar evento reminder_created", flush=True)
            publisher.notify({
                "type": "reminder_created",
                "recordatorio_id": nuevo_id,
                "medicamento_id": medicamento_id,
                "paciente_id": paciente_id,
                "hora_recordatorio": data["hora_recordatorio"].strip(),
                "fecha_inicio": data["fecha_inicio"].strip(),
                "activo": int(data.get("activo", 1)),
                "observaciones": data.get("observaciones", "").strip()
            })
        else:
            print("publisher es None", flush=True)

        
        return {
            "mensaje": "Recordatorio creado correctamente",
            "recordatorio_id": nuevo_id
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="medicamento_id debe ser un entero valido")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al crear el recordatorio: {e}")
    finally:
        conn.close()


@router.get("/{paciente_id}")
def listar_recordatorios(paciente_id: int):
    try:
        filas = get_recordatorios_por_paciente(paciente_id)

        recordatorios = []
        for fila in filas:
            recordatorios.append({
                "id": fila["id"],
                "medicamento_id": fila["medicamento_id"],
                "medicamento_nombre": fila["medicamento_nombre"],
                "dosis": fila["dosis"],
                "hora_recordatorio": fila["hora_recordatorio"],
                "fecha_inicio": fila["fecha_inicio"],
                "activo": fila["activo"],
                "observaciones": fila["observaciones"]
            })

        return {"recordatorios": recordatorios}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener recordatorios: {e}")


<<<<<<< HEAD
@router.get("/panel-dia/{paciente_id}")
def obtener_panel_dia(paciente_id: int):
    try:
        filas = get_panel_dia_por_paciente(paciente_id)

        recordatorios = []
        for fila in filas:
            recordatorios.append({
                "recordatorio_id": fila["recordatorio_id"],
                "paciente_id": fila["paciente_id"],
                "medicamento_id": fila["medicamento_id"],
                "medicamento_nombre": fila["medicamento_nombre"],
                "dosis": fila["dosis"],
                "hora_recordatorio": fila["hora_recordatorio"],
                "fecha_inicio": fila["fecha_inicio"],
                "activo": fila["activo"],
                "observaciones": fila["observaciones"],
                "fecha_programada": fila["fecha_programada"],
                "toma_id": fila["toma_id"],
                "fecha_hora_toma": fila["fecha_hora_toma"],
                "estado_toma": fila["estado_toma"],
                "tomada": bool(fila["tomada"])
            })

        return {"recordatorios": recordatorios}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener panel del día: {e}")
=======
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
>>>>>>> 746f323ecd9223321641613fefa868daec13de58
