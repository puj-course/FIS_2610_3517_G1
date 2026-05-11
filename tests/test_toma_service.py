########################################################################################
#   test_toma_service.py
########################################################################################

from unittest.mock import Mock

import pytest
from bson import ObjectId

from backend.services import toma_service as toma_service_module
from backend.services.toma_service import TomaService


# =========================
# IDS DE PRUEBA TIPO MONGODB
# =========================

# Después de la migración a MongoDB, las entidades principales usan ObjectId.
# Por eso los datos de prueba se construyen con strings que tienen formato válido
# de ObjectId.
PACIENTE_ID_VALIDO = "507f1f77bcf86cd799439011"
MEDICAMENTO_ID_VALIDO = "507f1f77bcf86cd799439012"
RECORDATORIO_ID_VALIDO = "507f1f77bcf86cd799439013"
TOMA_ID_VALIDO = "507f1f77bcf86cd799439014"

OTRO_PACIENTE_ID = "507f1f77bcf86cd799439021"
OTRO_MEDICAMENTO_ID = "507f1f77bcf86cd799439022"
OTRO_RECORDATORIO_ID = "507f1f77bcf86cd799439023"


# =========================
# COLECCIONES FALSAS
# =========================

class ResultadoInsertOneFalso:
    """
    Resultado falso de MongoDB para insert_one().

    MongoDB normalmente devuelve un objeto con inserted_id. El servicio usa
    ese inserted_id para construir la respuesta.
    """

    def __init__(self, inserted_id=TOMA_ID_VALIDO):
        self.inserted_id = ObjectId(inserted_id)


class CursorFalso(list):
    """
    Cursor falso para simular el cursor de MongoDB.

    TomaService usa:
        tomas_col.find(...).sort(...)

    Una lista normal no tiene sort con la misma firma de MongoDB, por eso
    esta clase implementa un sort compatible con el uso del servicio.
    """

    def sort(self, campo, direccion):
        reverse = direccion == -1

        return CursorFalso(
            sorted(
                self,
                key=lambda doc: doc.get(campo, ""),
                reverse=reverse
            )
        )


class ColeccionFalsa:
    """
    Colección falsa para simular una colección de MongoDB.

    Esta clase reemplaza:
        pacientes_col
        medicamentos_col
        recordatorios_col
        tomas_col

    durante las pruebas.

    Implementa los métodos usados por TomaService:
        find_one()
        find()
        insert_one()
    """

    def __init__(self, documentos=None, inserted_id=TOMA_ID_VALIDO, error_insert=None):
        self.documentos = documentos or []
        self.inserted_id = inserted_id
        self.error_insert = error_insert
        self.documento_insertado = None
        self.filtro_find_one = None
        self.filtro_find = None

    def _coincide(self, documento, filtro):
        """
        Verifica si un documento cumple un filtro simple.

        Soporta igualdad directa y también el caso:
            {"fecha_programada": {"$regex": "^2026-04-12"}}
        usado por obtener_tomas_del_dia().
        """
        filtro = filtro or {}

        for clave, valor in filtro.items():
            valor_documento = documento.get(clave)

            if isinstance(valor, dict) and "$regex" in valor:
                prefijo = valor["$regex"].replace("^", "")
                if not str(valor_documento).startswith(prefijo):
                    return False

            elif valor_documento != valor:
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

        Retorna un CursorFalso para permitir encadenar .sort().
        """
        self.filtro_find = filtro or {}

        return CursorFalso([
            documento
            for documento in self.documentos
            if self._coincide(documento, self.filtro_find)
        ])

    def insert_one(self, documento):
        """
        Simula insert_one() de MongoDB.

        Si error_insert está definido, lanza ese error. Esto permite probar
        errores de base de datos sin usar una base real.
        """
        if self.error_insert:
            raise self.error_insert

        documento_con_id = {
            "_id": ObjectId(self.inserted_id),
            **documento
        }

        self.documento_insertado = documento_con_id
        self.documentos.append(documento_con_id)

        return ResultadoInsertOneFalso(self.inserted_id)


# =========================
# DOCUMENTOS BASE
# =========================

def paciente_mongo(paciente_id=PACIENTE_ID_VALIDO):
    """
    Documento de paciente simulado en MongoDB.
    """
    return {
        "_id": ObjectId(paciente_id),
        "nombres": "Paciente prueba"
    }


def medicamento_mongo(
    medicamento_id=MEDICAMENTO_ID_VALIDO,
    paciente_id=PACIENTE_ID_VALIDO
):
    """
    Documento de medicamento simulado en MongoDB.

    El campo paciente_id permite validar si el medicamento pertenece
    al paciente correcto.
    """
    return {
        "_id": ObjectId(medicamento_id),
        "nombre": "Aspirina",
        "paciente_id": paciente_id
    }


def recordatorio_mongo(
    recordatorio_id=RECORDATORIO_ID_VALIDO,
    medicamento_id=MEDICAMENTO_ID_VALIDO
):
    """
    Documento de recordatorio simulado en MongoDB.

    El campo medicamento_id permite validar si el recordatorio pertenece
    al medicamento correcto.
    """
    return {
        "_id": ObjectId(recordatorio_id),
        "medicamento_id": medicamento_id
    }


def toma_mongo():
    """
    Documento de toma simulado en MongoDB.

    Se usa principalmente para probar duplicados.
    """
    return {
        "_id": ObjectId(TOMA_ID_VALIDO),
        "paciente_id": PACIENTE_ID_VALIDO,
        "medicamento_id": MEDICAMENTO_ID_VALIDO,
        "recordatorio_id": RECORDATORIO_ID_VALIDO,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
        "diferencia_minutos": 3.0,
        "estado": "a_tiempo",
        "observaciones": "Prueba automatizada"
    }


def datos_validos():
    """
    Datos válidos para registrar una toma.

    Se usan en casi todas las pruebas. Cada test modifica una copia
    cuando necesita probar un caso inválido.
    """
    return {
        "paciente_id": PACIENTE_ID_VALIDO,
        "medicamento_id": MEDICAMENTO_ID_VALIDO,
        "recordatorio_id": RECORDATORIO_ID_VALIDO,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba automatizada",
    }


# =========================
# FIXTURE PRINCIPAL
# =========================

@pytest.fixture
def colecciones_mongo(monkeypatch):
    """
    Fixture que reemplaza las colecciones reales de MongoDB por colecciones falsas.

    Antes estos tests creaban una base SQLite temporal con DB_PATH.
    Eso ya no aplica porque TomaService fue migrado a MongoDB y usa:

        pacientes_col
        medicamentos_col
        recordatorios_col
        tomas_col

    directamente desde backend.database.
    """
    pacientes = ColeccionFalsa([
        paciente_mongo()
    ])

    medicamentos = ColeccionFalsa([
        medicamento_mongo(),
        medicamento_mongo(
            medicamento_id=OTRO_MEDICAMENTO_ID,
            paciente_id=OTRO_PACIENTE_ID
        )
    ])

    recordatorios = ColeccionFalsa([
        recordatorio_mongo(),
        recordatorio_mongo(
            recordatorio_id=OTRO_RECORDATORIO_ID,
            medicamento_id=OTRO_MEDICAMENTO_ID
        )
    ])

    tomas = ColeccionFalsa([])

    monkeypatch.setattr(toma_service_module, "pacientes_col", pacientes)
    monkeypatch.setattr(toma_service_module, "medicamentos_col", medicamentos)
    monkeypatch.setattr(toma_service_module, "recordatorios_col", recordatorios)
    monkeypatch.setattr(toma_service_module, "tomas_col", tomas)
    monkeypatch.setattr(toma_service_module, "publisher", None)

    return {
        "pacientes": pacientes,
        "medicamentos": medicamentos,
        "recordatorios": recordatorios,
        "tomas": tomas
    }


# =========================
# REGISTRO EXITOSO
# =========================

def test_registrar_toma_exitoso(colecciones_mongo, monkeypatch):
    """
    CASO VÁLIDO: registrar una toma correctamente.

    El servicio debe:
    1. Validar campos obligatorios.
    2. Verificar que el paciente existe.
    3. Verificar que el medicamento existe.
    4. Verificar que el medicamento pertenece al paciente.
    5. Verificar que el recordatorio existe.
    6. Verificar que el recordatorio pertenece al medicamento.
    7. Verificar que no exista una toma duplicada.
    8. Insertar la toma en tomas_col.
    9. Notificar con publisher si está disponible.
    """
    publisher_falso = Mock()
    monkeypatch.setattr(toma_service_module, "publisher", publisher_falso)

    resultado = TomaService().registrar_toma(**datos_validos())

    assert resultado["ok"] is True
    assert resultado["mensaje"] == "Toma registrada correctamente"
    assert resultado["toma_id"] == TOMA_ID_VALIDO

    assert resultado["data"]["paciente_id"] == PACIENTE_ID_VALIDO
    assert resultado["data"]["medicamento_id"] == MEDICAMENTO_ID_VALIDO
    assert resultado["data"]["recordatorio_id"] == RECORDATORIO_ID_VALIDO
    assert resultado["data"]["fecha_programada"] == "2026-04-12 08:00:00"
    assert resultado["data"]["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert resultado["data"]["estado"] == "a_tiempo"
    assert resultado["data"]["diferencia_minutos"] == 3.0
    assert resultado["data"]["observaciones"] == "Prueba automatizada"

    publisher_falso.notify.assert_called_once()

    evento = publisher_falso.notify.call_args.args[0]

    assert evento["type"] == "medication_taken"
    assert evento["toma_id"] == TOMA_ID_VALIDO
    assert evento["paciente_id"] == PACIENTE_ID_VALIDO
    assert evento["medicamento_id"] == MEDICAMENTO_ID_VALIDO
    assert evento["recordatorio_id"] == RECORDATORIO_ID_VALIDO
    assert evento["fecha_programada"] == "2026-04-12 08:00:00"
    assert evento["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert evento["estado"] == "a_tiempo"
    assert evento["diferencia_minutos"] == 3.0
    assert evento["observaciones"] == "Prueba automatizada"

    toma_insertada = colecciones_mongo["tomas"].documento_insertado

    assert toma_insertada is not None
    assert toma_insertada["paciente_id"] == PACIENTE_ID_VALIDO
    assert toma_insertada["medicamento_id"] == MEDICAMENTO_ID_VALIDO
    assert toma_insertada["recordatorio_id"] == RECORDATORIO_ID_VALIDO


# =========================
# VALIDACIONES DE CAMPOS OBLIGATORIOS
# =========================

def test_paciente_id_obligatorio(colecciones_mongo):
    data = datos_validos()
    data["paciente_id"] = None

    with pytest.raises(ValueError, match="paciente_id"):
        TomaService().registrar_toma(**data)


def test_medicamento_id_obligatorio(colecciones_mongo):
    data = datos_validos()
    data["medicamento_id"] = ""

    with pytest.raises(ValueError, match="medicamento_id"):
        TomaService().registrar_toma(**data)


def test_recordatorio_id_obligatorio(colecciones_mongo):
    data = datos_validos()
    data["recordatorio_id"] = ""

    with pytest.raises(ValueError, match="recordatorio_id"):
        TomaService().registrar_toma(**data)


def test_fecha_programada_obligatoria(colecciones_mongo):
    data = datos_validos()
    data["fecha_programada"] = "   "

    with pytest.raises(ValueError, match="fecha_programada"):
        TomaService().registrar_toma(**data)


def test_fecha_hora_toma_obligatoria(colecciones_mongo):
    data = datos_validos()
    data["fecha_hora_toma"] = ""

    with pytest.raises(ValueError, match="fecha_hora_toma"):
        TomaService().registrar_toma(**data)


def test_estado_obligatorio(colecciones_mongo):
    data = datos_validos()
    data["estado"] = ""

    with pytest.raises(ValueError, match="estado"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACIONES DE EXISTENCIA
# =========================

def test_paciente_no_existe(colecciones_mongo):
    data = datos_validos()
    data["paciente_id"] = OTRO_PACIENTE_ID

    with pytest.raises(LookupError, match="paciente no existe"):
        TomaService().registrar_toma(**data)


def test_medicamento_no_existe(colecciones_mongo):
    data = datos_validos()
    data["medicamento_id"] = "507f1f77bcf86cd799439099"

    with pytest.raises(LookupError, match="medicamento no existe"):
        TomaService().registrar_toma(**data)


def test_recordatorio_no_existe(colecciones_mongo):
    data = datos_validos()
    data["recordatorio_id"] = "507f1f77bcf86cd799439099"

    with pytest.raises(LookupError, match="recordatorio no existe"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACIONES DE RELACIÓN ENTRE ENTIDADES
# =========================

def test_medicamento_no_pertenece_al_paciente(colecciones_mongo):
    """
    El medicamento existe, pero pertenece a otro paciente.
    """
    data = datos_validos()
    data["medicamento_id"] = OTRO_MEDICAMENTO_ID

    with pytest.raises(ValueError, match="no pertenece al paciente"):
        TomaService().registrar_toma(**data)


def test_recordatorio_no_pertenece_al_medicamento(colecciones_mongo):
    """
    El recordatorio existe, pero pertenece a otro medicamento.
    """
    data = datos_validos()
    data["recordatorio_id"] = OTRO_RECORDATORIO_ID

    with pytest.raises(ValueError, match="no pertenece al medicamento"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACIÓN DE DUPLICADOS
# =========================

def test_toma_duplicada_lanza_error(colecciones_mongo):
    """
    Si ya existe una toma para el mismo recordatorio y la misma fecha_programada,
    el servicio debe lanzar FileExistsError.
    """
    colecciones_mongo["tomas"].documentos.append(toma_mongo())

    with pytest.raises(FileExistsError, match="Ya existe una toma"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# ERRORES DE BASE DE DATOS
# =========================

def test_error_base_datos_lanza_runtime_error(monkeypatch):
    """
    Simula un error al insertar en tomas_col.

    En la versión anterior se intentaba forzar un error con una ruta SQLite
    inválida usando DB_PATH. Eso ya no aplica porque el servicio usa MongoDB.

    Ahora se simula el error directamente en tomas_col.insert_one().
    """
    pacientes = ColeccionFalsa([
        paciente_mongo()
    ])

    medicamentos = ColeccionFalsa([
        medicamento_mongo()
    ])

    recordatorios = ColeccionFalsa([
        recordatorio_mongo()
    ])

    tomas = ColeccionFalsa(
        [],
        error_insert=RuntimeError("Error de base de datos")
    )

    monkeypatch.setattr(toma_service_module, "pacientes_col", pacientes)
    monkeypatch.setattr(toma_service_module, "medicamentos_col", medicamentos)
    monkeypatch.setattr(toma_service_module, "recordatorios_col", recordatorios)
    monkeypatch.setattr(toma_service_module, "tomas_col", tomas)
    monkeypatch.setattr(toma_service_module, "publisher", None)

    with pytest.raises(RuntimeError, match="Error de base de datos"):
        TomaService().registrar_toma(**datos_validos())



