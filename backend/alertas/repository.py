from datetime import datetime, timezone

from backend.database import alertas_col


def guardar_alerta(
    tipo,
    mensaje,
    severidad,
    paciente_id,
    medicamento_id=None,
    recordatorio_id=None,
):
    alerta = {
        "tipo": tipo,
        "mensaje": mensaje,
        "severidad": severidad,
        "paciente_id": str(paciente_id) if paciente_id else None,
        "medicamento_id": str(medicamento_id) if medicamento_id else None,
        "recordatorio_id": str(recordatorio_id) if recordatorio_id else None,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    }

    alertas_col.insert_one(alerta)