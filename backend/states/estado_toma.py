from abc import ABC, abstractmethod

class EstadoToma(ABC):
    #clase abstracta que define la interfaz común para los posibles estados de la toma de medicamentos
    #usare el patron de diseño de strategy (comportamental
    @abstractmethod
    #ahora esta funcion lo que hace es devolver el nombre del estado actual de la toma de medicamentos como pendiente, tomada o asi
    def tomar_medicamento(self)->str:
        pass    
    class EstadoPendiente(EstadoToma):
        #estado de una toma cuya hora programada aun no ha llegado o lleva menos de 60 minutos de retraso sin ser marcada
        def tomar_medicamento(self) -> str:
            return "pendiente"