from abc import ABC, abstractmethod
from datetime import datetime


class EstadoToma(ABC):
    # Clase abstracta que define la interfaz común para los posibles estados
    @abstractmethod
    def obtener_estado(self) -> str:
        pass


class EstadoPendiente(EstadoToma):
    # Estado de una toma cuya hora programada aún no ha llegado
    # o lleva menos de 60 minutos de retraso sin ser marcada
    def obtener_estado(self) -> str:
        return "pendiente"


class EstadoTomado(EstadoToma):
    # Estado de una toma que se marca como administrada correctamente
    def obtener_estado(self) -> str:
        return "tomado"


class EstadoRetrasado(EstadoToma):
    # Estado de una toma cuando pasaron más de 60 minutos
    # desde la hora programada sin ser marcada como tomada
    UMBRAL_MINUTOS = 60

    def obtener_estado(self) -> str:
        return "atrasado"


def calcular_estado(medicamento: dict, hora_actual: datetime, tomas_del_dia: list) -> str:
    """
    Determina el estado de una toma comparando la hora programada con la hora actual
    y verificando si ya fue registrada como tomada.
    """

    # Verificar si ya fue marcada como tomada en la BD
    for toma in tomas_del_dia:
        if toma["medicamento_id"] == medicamento["id"] and toma["estado"] == "tomado":
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
        return EstadoPendiente().obtener_estado()  # hora malformada -> pendiente

    diferencia_minutos = (hora_actual - hora_med).total_seconds() / 60

    if diferencia_minutos > EstadoRetrasado.UMBRAL_MINUTOS:
        return EstadoRetrasado().obtener_estado()

    return EstadoPendiente().obtener_estado()