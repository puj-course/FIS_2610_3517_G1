from abc import ABC, abstractmethod 
class Historial(ABC):
    #interfaz base que define lo de cualquier historial de tomas
    #uso patron decorator porque se pueden agregar funcionalidades a los historiales de tomas sin modificar su estructura base
    @abstractmethod
    def get_obtener_datos(self)->dict:
        #esto me devuelve un diccionario con los datos del historial de tomas, como fecha, hora, medicamento, dosis, etc
        pass