# paciente_factory.py
# Patron Abstract Factory para la construcción de objetos Paciente (HU-27)
from abc import ABC, abstractmethod

# Clase base abstracta que define la interfaz común de cualquier tipo de paciente
class Paciente(ABC):
    @abstractmethod
    def como_tupla(self) -> tuple:
        """Devuelve los campos del paciente como tupla para el INSERT en SQLite."""
        pass

    @abstractmethod
    def como_dict(self) -> dict:
        """Devuelve los campos del paciente como diccionario para MongoDB."""
        pass

# Clase concreta que representa un paciente general
class PacienteGeneral(Paciente):
    def __init__(
        self,
        nombres: str,
        apellidos: str,
        fecha_nacimiento: str,
        genero: str,
        tipo_documento: str,
        numero_documento: str,
        telefono_contacto: str,
        eps_aseguradora: str,
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

    def como_tupla(self) -> tuple:
        # Devuelve los campos como tupla para INSERT en SQLite
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

    def como_dict(self) -> dict:
        # Devuelve los campos como diccionario para MongoDB
        return {
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "fecha_nacimiento": self.fecha_nacimiento,
            "genero": self.genero,
            "tipo_documento": self.tipo_documento,
            "numero_documento": self.numero_documento,
            "telefono_contacto": self.telefono_contacto,
            "eps_aseguradora": self.eps_aseguradora,
            "diagnostico_principal": self.diagnostico_principal,
            "alergias_conocidas": self.alergias_conocidas,
            "observaciones_adicionales": self.observaciones_adicionales,
        }

# Fábrica abstracta
class PacienteFactory(ABC):
    @abstractmethod
    def crear(self, data: dict) -> Paciente:
        pass

# Fábrica concreta para pacientes generales
class PacienteGeneralFactory(PacienteFactory):
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