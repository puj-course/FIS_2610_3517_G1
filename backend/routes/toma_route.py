from fastapi import APIRouter
from datetime import date
from backend.toma_repository import TomaRepository
from backend.models import get_connection

# Decorators (HU-37)
from backend.decorators.historial import (
    HistorialTomas,
    CumplimientoDecorator,
    AlertasDecorator
)

router = APIRouter(prefix="/tomas", tags=["Tomas"])

repositorio = TomaRepository()


# =========================
# REGISTRAR TOMA
# =========================
@router.post("/", status_code=201)
def registrar_toma(datos: dict):
    """
    Registra una nueva toma de medicamento.
    """
    toma_id = repositorio.registrar_toma(
        medicamento_id=datos.get("medicamento_id"),
        paciente_id=datos.get("paciente_id"),
        fecha=datos.get("fecha", str(date.today())),
        hora_programada=datos.get("hora_programada"),
        hora_tomada=datos.get("hora_tomada"),
        estado=datos.get("estado", "pendiente"),
        observaciones=datos.get("observaciones")
    )

    return {
        "message": "Toma registrada exitosamente",
        "toma_id": toma_id
    }


# =========================
# TOMAS DEL DÍA (CORREGIDO)
# =========================
@router.get("/dia/{paciente_id}")
def obtener_tomas(paciente_id: int, fecha: str = None):
    """
    Retorna las tomas del día de un paciente.
    """
    if not fecha:
        fecha = str(date.today())

    tomas = repositorio.obtener_tomas_del_dia(paciente_id, fecha)

    return {
        "tomas": [dict(t) for t in tomas]
    }


# =========================
# HISTORIAL COMPLETO (HU-36 + HU-37)
# =========================
@router.get("/historial/{paciente_id}")
def obtener_historial(paciente_id: int):
    """
    Retorna el historial completo de tomas de un paciente
    usando patrón Decorator (cumplimiento + alertas)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            t.id,
            t.paciente_id,
            t.medicamento_id,
            m.nombre AS medicamento_nombre,
            t.fecha,
            t.hora_programada,
            t.hora_tomada,
            t.estado,
            t.observaciones
        FROM tomas t
        INNER JOIN medicamentos m ON t.medicamento_id = m.id
        WHERE t.paciente_id = ?
        ORDER BY t.fecha DESC
    """, (paciente_id,))

    filas = cursor.fetchall()
    conn.close()

    historial = [dict(f) for f in filas]

    # ✅ SI NO HAY DATOS (evita errores)
    if not historial:
        return {
            "historial": [],
            "cumplimiento": {
                "total_tomas": 0,
                "tomas_realizadas": 0,
                "porcentaje": 0
            },
            "alertas": []
        }

    # =========================
    # APLICAR DECORATORS
    # =========================
    historial_base = HistorialTomas(historial)

    historial_decorado = CumplimientoDecorator(historial_base)
    historial_decorado = AlertasDecorator(historial_decorado)

    return historial_decorado.obtener_datos()