from backend.models import get_connection


class AlertRepository:
    def save_alert(
        self,
        tipo: str,
        mensaje: str,
        severidad: str,
        paciente_id: int,
        medicamento_id: int | None = None,
        recordatorio_id: int | None = None
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO alertas (
                    tipo,
                    mensaje,
                    severidad,
                    paciente_id,
                    medicamento_id,
                    recordatorio_id,
                    fecha_creacion,
                    atendida
                )
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 0)
            """, (
                tipo,
                mensaje,
                severidad,
                paciente_id,
                medicamento_id,
                recordatorio_id
            ))
            conn.commit()
        finally:
            conn.close()
