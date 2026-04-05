from backend.alertas.interfaces import IAlertObserver

class MedicationAlertObserver(IAlertObserver):
    def update(self, event: dict):
        if event.get("type") != "medication_registered":
            return

        print("MedicationAlertObserver recibió evento:", event)


class ReminderAlertObserver(IAlertObserver):
    def update(self, event: dict):
        if event.get("type") != "reminder_created":
            return

        print("ReminderAlertObserver recibió evento:", event)
