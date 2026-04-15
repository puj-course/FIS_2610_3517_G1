#################################################################################
#	El módulo abc en Python (Abstract Base Classes) permite definir clases 
#	base abstractas, que son plantillas que no se pueden instanciar directamente
#	 y que obligan a las subclases a implementar ciertos métodos. 
###############################################################################

from abc import ABC, abstractmethod

class IAlertObserver(ABC):
    @abstractmethod
    def update(self, event: dict):
        pass #hay que completar
