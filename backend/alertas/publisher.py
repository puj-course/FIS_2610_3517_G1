##############################################################################################
#
#
##############################################################################################
from backend.alertas.interfaces import IAlertObserver

class AlertPublisher:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer: IAlertObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: IAlertObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: dict):
        for observer in self._observers:
            observer.update(event)
