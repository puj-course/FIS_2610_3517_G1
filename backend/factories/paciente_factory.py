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

    #ahora creo la clase concreta PacienteGeneral, que hereda de Paciente y representa un paciente general, con sus campos específicos
class PacienteGeneral(Paciente):
    """
    representa un paciente general, con sus campos específicos ya validados desde la fábrica.
    """
    def __init__(self,nombres: str,apellidos: str,fecha_nacimiento: str,genero: str,tipo_documento: str,numero_documento: str,telefono_contacto: str,eps_aseguradora: str,
        diagnostico_principal: str,
        alergias_conocidas: str,
        observaciones_adicionales: str,
    ):
        self.nombres = nombres
        self.apellidos = apellidos
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        self.tipo_documento = tipo_documento
        self.numero_documento = numero_documento
        self.telefono_contacto = telefono_contacto
        self.eps_aseguradora = eps_aseguradora
        self.diagnostico_principal = diagnostico_principal
        self.alergias_conocidas = alergias_conocidas
        self.observaciones_adicionales = observaciones_adicionales
    def como_tupla(self) -> tuple: #este metodo devuelve los campos del paciente como tupla, en el orden que se necesita para el INSERT en la BD
        return (
            self.nombres,
            self.apellidos,
            self.fecha_nacimiento,
            self.genero,
            self.tipo_documento,
            self.numero_documento,
            self.telefono_contacto,
            self.eps_aseguradora,
            self.diagnostico_principal,
            self.alergias_conocidas,
            self.observaciones_adicionales,
        )
    
