from backend.alertas.interfaces import IAlertObserver
from backend.alertas.repository import guardar_alerta

class MedicationAlertObserver(IAlertObserver):
    def update(self, event: dict):
        mensaje = f"Se registró el medicamento {event.get('nombre')} para el paciente {event.get('paciente_id')}"

        guardar_alerta(
            tipo="medication_registered",
            mensaje=mensaje,
            severidad="media",
            paciente_id=event.get("paciente_id"),
            medicamento_id=event.get("medicamento_id")
        )


class ReminderAlertObserver(IAlertObserver):
    def update(self, event: dict):
        mensaje = f"Se creó un recordatorio para el medicamento {event.get('medicamento_id')}"

        guardar_alerta(
            tipo="reminder_created",
            mensaje=mensaje,
            severidad="baja",
            paciente_id=event.get("paciente_id"),
            medicamento_id=event.get("medicamento_id"),
            recordatorio_id=event.get("recordatorio_id")
        )