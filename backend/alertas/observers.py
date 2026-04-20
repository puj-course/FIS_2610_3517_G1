from backend.alertas.interfaces import IAlertObserver
from backend.alertas.repository import AlertRepository


class MedicationAlertObserver(IAlertObserver):
    def __init__(self):
        self.repository = AlertRepository()

    def update(self, event: dict):
        if event.get("type") != "medication_taken":
            return

        self.repository.save_alert(
            tipo="medication_taken",
            mensaje=(
                f"Se registró una toma del medicamento {event.get('medicamento_id')} "
                f"para el paciente {event.get('paciente_id')} en {event.get('fecha_hora_toma')}"
            ),
            severidad="info",
            paciente_id=event.get("paciente_id"),
            medicamento_id=event.get("medicamento_id"),
            recordatorio_id=event.get("recordatorio_id")
        )


class ReminderAlertObserver(IAlertObserver):
    def __init__(self):
        self.repository = AlertRepository()

    def update(self, event: dict):
        if event.get("type") != "reminder_created":
            return

        self.repository.save_alert(
            tipo="reminder_created",
            mensaje=(
                f"Se creó un recordatorio para el medicamento {event.get('medicamento_id')} "
                f"del paciente {event.get('paciente_id')} a las {event.get('hora_recordatorio')}"
            ),
            severidad="info",
            paciente_id=event.get("paciente_id"),
            medicamento_id=event.get("medicamento_id"),
            recordatorio_id=event.get("recordatorio_id")
        )
