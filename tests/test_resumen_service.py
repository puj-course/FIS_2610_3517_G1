########################################################################################
#   test_resumen_service.py
########################################################################################

import pytest
from bson import ObjectId

from backend.services import resumen_paciente_service as resumen_module
from backend.services.resumen_paciente_service import ResumenPacienteService


# =========================
# IDS DE PRUEBA TIPO MONGODB
# =========================

PACIENTE_ID_VALIDO = "507f1f77bcf86cd799439011"
PACIENTE_ID_SIN_DATOS = "507f1f77bcf86cd799439012"
PACIENTE_ID_INEXISTENTE = "507f1f77bcf86cd799439099"

MEDICAMENTO_ID_VALIDO = "507f1f77bcf86cd799439021"
TOMA_ID_1 = "507f1f77bcf86cd799439031"
TOMA_ID_2 = "507f1f77bcf86cd799439032"


# =========================
# COLECCIÓN FALSA PARA MONGODB
# =========================

class ColeccionFalsa:
    """
    Colección falsa para simular una colección de MongoDB.

    El servicio ResumenPacienteService ya no usa SQLite ni get_connection.
    Ahora consulta directamente:

        pacientes_col
        medicamentos_col
        tomas_col

    Por eso esta clase implementa los métodos mínimos que usa el servicio:
        - find_one()
        - find()
    """

    def __init__(self, documentos=None):
        self.documentos = documentos or []
        self.filtro_find_one = None
        self.filtro_find = None

    def _coincide(self, documento, filtro):
        """
        Verifica si un documento cumple un filtro simple de igualdad.

        Ejemplos de filtros usados por el servicio:
            {"_id": ObjectId(paciente_id)}
            {"paciente_id": paciente_id}
        """
        filtro = filtro or {}

        for clave, valor in filtro.items():
            if documento.get(clave) != valor:
                return False

        return True

    def find_one(self, filtro):
        """
        Simula find_one() de MongoDB.

        Retorna el primer documento que coincida con el filtro.
        Si no encuentra ninguno, retorna None.
        """
        self.filtro_find_one = filtro

        for documento in self.documentos:
            if self._coincide(documento, filtro):
                return documento

        return None

    def find(self, filtro=None):
        """
        Simula find() de MongoDB.

        Retorna una lista de documentos que cumplen el filtro.
        """
        self.filtro_find = filtro or {}

        return [
            documento
            for documento in self.documentos
            if self._coincide(documento, self.filtro_find)
        ]


# =========================
# DOCUMENTOS BASE
# =========================

def paciente_mongo():
    """
    Paciente principal usado en las pruebas.
    """
    return {
        "_id": ObjectId(PACIENTE_ID_VALIDO),
        "nombres": "Ana",
        "apellidos": "Lopez",
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension",
    }


def paciente_sin_datos_mongo():
    """
    Paciente válido, pero sin medicamentos ni historial de tomas.

    Sirve para probar el resumen vacío.
    """
    return {
        "_id": ObjectId(PACIENTE_ID_SIN_DATOS),
        "nombres": "Carlos",
        "apellidos": "Perez",
        "tipo_documento": "CC",
        "numero_documento": "87654321",
        "telefono_contacto": "3111234567",
        "eps_aseguradora": "Nueva EPS",
        "diagnostico_principal": "Diabetes",
    }


def medicamento_mongo():
    """
    Medicamento activo asociado al paciente principal.
    """
    return {
        "_id": ObjectId(MEDICAMENTO_ID_VALIDO),
        "nombre": "Aspirina",
        "dosis": "500 mg",
        "frecuencia": "Cada 8 horas",
        "horario": "08:00",
        "fecha_inicio": "2026-04-01",
        "observaciones": "Con comida",
        "paciente_id": PACIENTE_ID_VALIDO,
    }


def tomas_mongo():
    """
    Historial simulado de tomas del paciente.

    Incluye una toma realizada y una pendiente para calcular:
        total_tomas = 2
        tomas_realizadas = 1
        porcentaje = 50.0
    """
    return [
        {
            "_id": ObjectId(TOMA_ID_1),
            "paciente_id": PACIENTE_ID_VALIDO,
            "medicamento_id": MEDICAMENTO_ID_VALIDO,
            "nombre": "Aspirina",
            "fecha": "2026-04-12",
            "hora_programada": "08:00",
            "hora_tomada": "08:05",
            "estado": "tomado",
            "observaciones": "Tomada correctamente",
        },
        {
            "_id": ObjectId(TOMA_ID_2),
            "paciente_id": PACIENTE_ID_VALIDO,
            "medicamento_id": MEDICAMENTO_ID_VALIDO,
            "nombre": "Aspirina",
            "fecha": "2026-04-13",
            "hora_programada": "08:00",
            "hora_tomada": None,
            "estado": "pendiente",
            "observaciones": "Pendiente",
        },
    ]


# =========================
# FIXTURE DE COLECCIONES
# =========================

@pytest.fixture
def colecciones_mongo(monkeypatch):
    """
    Reemplaza las colecciones reales de MongoDB por colecciones falsas.

    Antes estos tests creaban una base SQLite temporal y parcheaban
    get_connection. Eso ya no aplica porque resumen_paciente_service.py
    trabaja directamente con colecciones MongoDB.
    """
    pacientes_col_falsa = ColeccionFalsa([
        paciente_mongo(),
        paciente_sin_datos_mongo(),
    ])

    medicamentos_col_falsa = ColeccionFalsa([
        medicamento_mongo(),
    ])

    tomas_col_falsa = ColeccionFalsa(tomas_mongo())

    monkeypatch.setattr(
        resumen_module,
        "pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        resumen_module,
        "medicamentos_col",
        medicamentos_col_falsa
    )

    monkeypatch.setattr(
        resumen_module,
        "tomas_col",
        tomas_col_falsa
    )

    return {
        "pacientes": pacientes_col_falsa,
        "medicamentos": medicamentos_col_falsa,
        "tomas": tomas_col_falsa,
    }


# =========================
# PACIENTE
# =========================

def test_paciente_ok(colecciones_mongo):
    """
    CASO VÁLIDO: obtener un paciente existente por ObjectId.
    """
    service = ResumenPacienteService()

    paciente = service.obtener_paciente(PACIENTE_ID_VALIDO)

    assert str(paciente["_id"]) == PACIENTE_ID_VALIDO
    assert paciente["nombres"] == "Ana"
    assert paciente["apellidos"] == "Lopez"


def test_paciente_none(colecciones_mongo):
    """
    CASO INVÁLIDO: el paciente no existe.
    """
    service = ResumenPacienteService()

    paciente = service.obtener_paciente(PACIENTE_ID_INEXISTENTE)

    assert paciente is None


# =========================
# MEDICAMENTOS
# =========================

def test_medicamentos_ok(colecciones_mongo):
    """
    CASO VÁLIDO: obtener medicamentos activos asociados al paciente.
    """
    service = ResumenPacienteService()

    medicamentos = service.obtener_medicamentos_activos(PACIENTE_ID_VALIDO)

    assert len(medicamentos) == 1
    assert medicamentos[0]["nombre"] == "Aspirina"
    assert medicamentos[0]["paciente_id"] == PACIENTE_ID_VALIDO


def test_medicamentos_vacio(colecciones_mongo):
    """
    CASO SIN MEDICAMENTOS: el paciente existe, pero no tiene medicamentos.
    """
    service = ResumenPacienteService()

    medicamentos = service.obtener_medicamentos_activos(PACIENTE_ID_SIN_DATOS)

    assert medicamentos == []


# =========================
# HISTORIAL
# =========================

def test_historial_ok(colecciones_mongo):
    """
    CASO VÁLIDO: obtener historial de tomas formateado.

    El servicio toma los documentos de tomas_col y construye una lista
    con los campos que necesita el resumen.
    """
    service = ResumenPacienteService()

    historial = service.obtener_historial_formateado(PACIENTE_ID_VALIDO)

    assert len(historial) == 2
    assert historial[0]["medicamento"] == "Aspirina"
    assert historial[0]["medicamento_nombre"] == "Aspirina"
    assert historial[0]["estado"] == "tomado"
    assert historial[1]["estado"] == "pendiente"


# =========================
# RESUMEN DEL PACIENTE
# =========================

def test_resumen_ok(colecciones_mongo):
    """
    CASO VÁLIDO: construir resumen completo del paciente.

    Debe incluir:
        - datos del paciente
        - medicamentos activos
        - historial
        - métricas de cumplimiento
        - alertas
    """
    service = ResumenPacienteService()

    resumen = service.construir_resumen(PACIENTE_ID_VALIDO)

    assert resumen["paciente"]["id"] == PACIENTE_ID_VALIDO
    assert resumen["paciente"]["nombres"] == "Ana"
    assert resumen["paciente"]["apellidos"] == "Lopez"

    assert len(resumen["medicamentos_activos"]) == 1
    assert resumen["medicamentos_activos"][0]["nombre"] == "Aspirina"

    assert len(resumen["historial"]) == 2
    assert resumen["cumplimiento"]["total_tomas"] == 2
    assert resumen["cumplimiento"]["tomas_realizadas"] == 1
    assert resumen["cumplimiento"]["porcentaje"] == 50.0

    # El servicio actual retorna alertas como lista vacía.
    assert resumen["alertas"] == []


def test_resumen_404(colecciones_mongo):
    """
    CASO INVÁLIDO: construir resumen de un paciente inexistente.

    Debe lanzar LookupError.
    """
    service = ResumenPacienteService()

    with pytest.raises(LookupError, match="Paciente no encontrado"):
        service.construir_resumen(PACIENTE_ID_INEXISTENTE)


def test_resumen_vacio(colecciones_mongo):
    """
    CASO VÁLIDO: paciente existente sin medicamentos ni historial.

    El resumen debe retornar listas vacías y porcentaje de cumplimiento 0.
    """
    service = ResumenPacienteService()

    resumen = service.construir_resumen(PACIENTE_ID_SIN_DATOS)

    assert resumen["paciente"]["id"] == PACIENTE_ID_SIN_DATOS
    assert resumen["paciente"]["nombres"] == "Carlos"
    assert resumen["medicamentos_activos"] == []
    assert resumen["historial"] == []
    assert resumen["cumplimiento"]["total_tomas"] == 0
    assert resumen["cumplimiento"]["porcentaje"] == 0
    assert resumen["alertas"] == []

