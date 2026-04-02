# Aqui usamos el patron Abstract Factory para la construcción de objetos Paciente (hu27)

from abc import ABC, abstractmethod

#creo la clase abstracta Paciente, que define la interfaz común para cualquier tipo de paciente (general, pediátrico, adulto mayor, etc.)
class Paciente(ABC):
    """
    Clase base abstracta que define la interfaz común de cualquier tipo de paciente.
    Todo tipo de paciente tiene que heredar de aquí 
    e implementar el metodo como_tupla(), para tener los valores en buen formato y poder insertarlos en la BD
    """
    @abstractmethod
    def como_tupla(self) -> tuple: ##aqui ese self es el objeto paciente, y el metodo como_tupla devuelve una tupla con los campos del paciente, para que se pueda usar en el INSERT de la BD
        """Devuelve los campos del paciente como tupla para el INSERT en la BD."""
        pass

