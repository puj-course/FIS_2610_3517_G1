from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.models import get_connection
from backend.historial_toma import HistorialTomaBuilder
from backend.validaciones import verificar_paciente_existe, verificar_medicamento_existe

router = APIRouter(prefix="/historial", tags=["Historial de tomas"])


class RegistrarTomaRequest(BaseModel):
    paciente_id:      int
    medicamento_id:   int
    recordatorio_id:  Optional[int] = None
    fecha_programada: str            # formato: "YYYY-MM-DD HH:MM:SS"
    fecha_hora_toma:  Optional[str] = None  # None si no se tomó (omitida)
    observaciones:    Optional[str] = None


@router.post("/", status_code=201)
def registrar_toma_historial(data: RegistrarTomaRequest):
    """
    Registra una toma en el historial usando el patrón Builder.
    Calcula automáticamente el estado (a_tiempo, tarde, omitida)
    y la diferencia en minutos.
    """
    conn = get_connection()
    try:
        # Validar que paciente y medicamento existan
        if not verificar_paciente_existe(data.paciente_id, conn):
            raise HTTPException(status_code=404, detail="El paciente no existe")
        if not verificar_medicamento_existe(data.medicamento_id, conn):
            raise HTTPException(status_code=404, detail="El medicamento no existe")

        # Construimos el objeto con el Builder
        try:
            toma = (
                HistorialTomaBuilder()
                .set_paciente(data.paciente_id)
                .set_medicamento(data.medicamento_id)
                .set_recordatorio(data.recordatorio_id)
                .set_fecha_programada(data.fecha_programada)
                .set_fecha_hora_toma(data.fecha_hora_toma)
                .set_observaciones(data.observaciones)
                .build()
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        cursor = conn.cursor()

        # Verificar duplicado
        cursor.execute("""
            SELECT id FROM historial_tomas
            WHERE recordatorio_id = ? AND fecha_programada = ?
        """, (toma.recordatorio_id, toma.fecha_programada))
        if cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Ya existe un registro para ese recordatorio y fecha programada"
            )

        cursor.execute("""
            INSERT INTO historial_tomas (
                paciente_id, medicamento_id, recordatorio_id,
                fecha_programada, fecha_hora_toma,
                diferencia_minutos, estado, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            toma.paciente_id,
            toma.medicamento_id,
            toma.recordatorio_id,
            toma.fecha_programada,
            toma.fecha_hora_toma,
            toma.diferencia_minutos,
            toma.estado,
            toma.observaciones
        ))
        conn.commit()
        nuevo_id = cursor.lastrowid

        return {
            "mensaje": "Toma registrada correctamente",
            "id":      nuevo_id,
            "toma":    toma.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        conn.close()


@router.get("/{paciente_id}")
def obtener_historial(paciente_id: int):
    """
    Devuelve el historial completo de tomas de un paciente,
    ordenado de más reciente a más antiguo.
    """
    conn = get_connection()
    try:
        if not verificar_paciente_existe(paciente_id, conn):
            raise HTTPException(status_code=404, detail="El paciente no existe")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.id,
                h.paciente_id,
                h.medicamento_id,
                m.nombre        AS medicamento_nombre,
                h.recordatorio_id,
                h.fecha_programada,
                h.fecha_hora_toma,
                h.diferencia_minutos,
                h.estado,
                h.observaciones
            FROM historial_tomas h
            INNER JOIN medicamentos m ON h.medicamento_id = m.id
            WHERE h.paciente_id = ?
            ORDER BY h.fecha_programada DESC
        """, (paciente_id,))

        filas = cursor.fetchall()
        historial = [dict(f) for f in filas]

        # Calculamos resumen de cumplimiento usando el decorador ya existente
        total   = len(historial)
        a_tiempo = sum(1 for t in historial if t["estado"] == "a_tiempo")
        tarde    = sum(1 for t in historial if t["estado"] == "tarde")
        omitidas = sum(1 for t in historial if t["estado"] == "omitida")
        porcentaje = round((a_tiempo + tarde) / total * 100, 1) if total > 0 else 0

        return {
            "historial": historial,
            "resumen": {
                "total":             total,
                "a_tiempo":          a_tiempo,
                "tarde":             tarde,
                "omitidas":          omitidas,
                "porcentaje_cumplimiento": porcentaje
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        conn.close()