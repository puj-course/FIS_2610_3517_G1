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
    #ahora creo la fabrica abstracta y concreta que son aquellas que se encargan de validar los datos de entrada y crear los objetos Paciente correspondientes, en este caso solo tengo una fabrica concreta para pacientes generales, pero se pueden crear otras fabricas concretas para otros tipos de pacientes (pediátricos, adultos mayores, etc.)
class PacienteFactory(ABC):
    """
    al ser la fabrica entonces para agregar un nuevo tipo de paciente en el futuro, solo se crea una nueva
    subclase de PacienteFactory y una nueva subclase de Paciente. La ruta NO cambia.
    """
    @abstractmethod
    def crear(self, data: dict) -> Paciente:
        """
        devuelve un objeto Paciente construido listo para persistirse en la BD.
        """
        pass
class PacienteGeneralFactory(PacienteFactory):
    """
    Fábrica concreta para pacientes generales.
    Centraliza toda la normalización de datos (strip, campos opcionales, etc.)
    que antes estaba  dispersa dentro del endpoint. es decir, ahora el endpoint solo se encarga de recibir los datos, 
    pasarlos a la fábrica y luego pasar el objeto Paciente a la capa de persistencia, sin preocuparse por la validación o normalización de los datos, 
    que es responsabilidad de la fábrica. Esto hace que el código sea más limpio, modular y fácil de mantener. 
    Si en el futuro se necesitan cambios en la forma de crear pacientes generales (agregar un nuevo campo obligatorio o cambiar la forma de validar un campo), solo se necesita modificar esta clase sin afectar el resto del código.
    """
    #en esta funcion quitamos espacios extrasy dejamos los datos en el formato correcto, ademas de manejar los campos opcionales con get() para evitar errores si no se envian, y finalmente creamos y devolvemos un objeto PacienteGeneral con los datos ya validados y normalizados.
    def crear(self, data: dict) -> PacienteGeneral:
        return PacienteGeneral(
            nombres=data["nombres"].strip(),
            apellidos=data["apellidos"].strip(),
            fecha_nacimiento=data["fecha_nacimiento"].strip(),
            genero=data["genero"].strip(),
            tipo_documento=data["tipo_documento"].strip(),
            numero_documento=data["numero_documento"].strip(),
            telefono_contacto=data["telefono_contacto"].strip(),
            eps_aseguradora=data.get("eps_aseguradora", "").strip(),
            diagnostico_principal=data.get("diagnostico_principal", "").strip(),
            alergias_conocidas=data.get("alergias_conocidas", "").strip(),
            observaciones_adicionales=data.get("observaciones_adicionales", "").strip(),
        )
