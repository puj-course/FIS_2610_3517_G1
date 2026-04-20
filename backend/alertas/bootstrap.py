from backend.alertas.publisher import AlertPublisher
from backend.alertas.observers import MedicationAlertObserver, ReminderAlertObserver

publisher = AlertPublisher()
publisher.subscribe(MedicationAlertObserver())
publisher.subscribe(ReminderAlertObserver())
