from abc import ABC, abstractmethod
from datetime import datetime
from backend.states.estado_toma import (EstadoToma, EstadoPendiente, EstadoTomada, EstadoRetrasado)

class EstadoToma(ABC):
    #clase abstracta que define la interfaz común para los posibles estados de la toma de medicamentos
    #usare el patron de diseño de strategy (comportamental
    @abstractmethod
    #ahora esta funcion lo que hace es devolver el nombre del estado actual de la toma de medicamentos como pendiente, tomada o asi
    def obtener_estado(self)->str:
        pass    
    class EstadoPendiente(EstadoToma):
        #estado de una toma cuya hora programada aun no ha llegado o lleva menos de 60 minutos de retraso sin ser marcada
        def obtener_estado(self) -> str:
            return "pendiente"
    class EstadoTomada(EstadoToma):
        #estado de una toma que se marca como administrada correctamente
        def obtener_estado(self) -> str:
            return "tomado"
    class EstadoRetrasado(EstadoToma):
        #estado de una toma cuando pasaron más de 60 minutos desde la hora programada sin ser marcada como tomada
        def obtener_estado(self) -> str:
            return "atrasado"
        
    
def calcular_estado(medicamento: dict, hora_actual: datetime, tomas_del_dia: list) -> str:
    ## Determina el estado de una toma comparando la hora programada con la hora actual y verificando si ya fue registrada como tomada.
    ##medicamento es un diccionario que representa un medicamento con al menos las claves 'id' y 'horario' (en formato 'HH:MM')
    ##hora_actual es un objeto datetime que representa la hora actual
    ##tomas_del_dia es una lista de diccionarios que representan las tomas registradas en la base de datos para el día actual, cada uno con al menos las claves 'medicamento_id' y 'estado'
    
    # Verificar si ya fue marcada como tomada en la BD
    for toma in tomas_del_dia:
        if (toma["medicamento_id"] == medicamento["id"] and toma["estado"] == "tomado"):
            return EstadoTomado().obtener_estado()

    # Convertir hora programada y calcular diferencia
    try:
        hora_med = datetime.strptime(medicamento["horario"], "%H:%M")
        hora_med = hora_actual.replace(
            hour=hora_med.hour,
            minute=hora_med.minute,
            second=0,
            microsecond=0
        )
    except ValueError:
        return EstadoPendiente().obtener_estado()  # hora malformada → pendiente

    diferencia_minutos = (hora_actual - hora_med).total_seconds() / 60

    if diferencia_minutos > EstadoAtrasado.UMBRAL_MINUTOS:
        return EstadoAtrasado().obtener_estado()

    return EstadoPendiente().obtener_estado()