########################################################################################
# test_toma_service.py
# Pruebas para TomaService usando MongoDB mockeado
########################################################################################

from unittest.mock import Mock, MagicMock
from bson import ObjectId
import pytest

from backend.services import toma_service as toma_service_module
from backend.services.toma_service import TomaService


# =========================
# IDS BASE
# =========================

PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
RECORDATORIO_ID = "69feb400322be070cd1c97cf"
TOMA_ID = ObjectId("69feb500322be070cd1c97d0")


# =========================
# FIXTURES Y DATOS BASE
# =========================

def datos_validos():
    return {
        "paciente_id": PACIENTE_ID,
        "medicamento_id": MEDICAMENTO_ID,
        "recordatorio_id": RECORDATORIO_ID,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba automatizada",
    }


@pytest.fixture
def colecciones_mock(monkeypatch):
    pacientes_col = MagicMock()
    medicamentos_col = MagicMock()
    recordatorios_col = MagicMock()
    tomas_col = MagicMock()

    pacientes_col.find_one.return_value = {
        "_id": ObjectId(PACIENTE_ID)
    }

    medicamentos_col.find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "paciente_id": PACIENTE_ID,
        "nombre": "Aspirina"
    }

    recordatorios_col.find_one.return_value = {
        "_id": ObjectId(RECORDATORIO_ID),
        "medicamento_id": MEDICAMENTO_ID
    }

    tomas_col.find_one.return_value = None

    insert_result = MagicMock()
    insert_result.inserted_id = TOMA_ID
    tomas_col.insert_one.return_value = insert_result

    monkeypatch.setattr(toma_service_module, "pacientes_col", pacientes_col)
    monkeypatch.setattr(toma_service_module, "medicamentos_col", medicamentos_col)
    monkeypatch.setattr(toma_service_module, "recordatorios_col", recordatorios_col)
    monkeypatch.setattr(toma_service_module, "tomas_col", tomas_col)

    return {
        "pacientes_col": pacientes_col,
        "medicamentos_col": medicamentos_col,
        "recordatorios_col": recordatorios_col,
        "tomas_col": tomas_col
    }


# =========================
# REGISTRO EXITOSO
# =========================

def test_registrar_toma_exitoso(colecciones_mock, monkeypatch):
    publisher_falso = Mock()
    monkeypatch.setattr(toma_service_module, "publisher", publisher_falso)

    resultado = TomaService().registrar_toma(**datos_validos())

    assert resultado["ok"] is True
    assert resultado["mensaje"] == "Toma registrada correctamente"
    assert resultado["toma_id"] == str(TOMA_ID)

    assert resultado["data"]["paciente_id"] == PACIENTE_ID
    assert resultado["data"]["medicamento_id"] == MEDICAMENTO_ID
    assert resultado["data"]["recordatorio_id"] == RECORDATORIO_ID
    assert resultado["data"]["fecha_programada"] == "2026-04-12 08:00:00"
    assert resultado["data"]["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert resultado["data"]["estado"] == "a_tiempo"
    assert resultado["data"]["diferencia_minutos"] == 3.0
    assert resultado["data"]["observaciones"] == "Prueba automatizada"

    colecciones_mock["tomas_col"].insert_one.assert_called_once()

    documento_insertado = colecciones_mock["tomas_col"].insert_one.call_args.args[0]

    assert documento_insertado["paciente_id"] == PACIENTE_ID
    assert documento_insertado["medicamento_id"] == MEDICAMENTO_ID
    assert documento_insertado["recordatorio_id"] == RECORDATORIO_ID
    assert documento_insertado["fecha_programada"] == "2026-04-12 08:00:00"
    assert documento_insertado["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert documento_insertado["estado"] == "a_tiempo"
    assert documento_insertado["diferencia_minutos"] == 3.0
    assert documento_insertado["observaciones"] == "Prueba automatizada"

    publisher_falso.notify.assert_called_once()

    evento = publisher_falso.notify.call_args.args[0]

    assert evento["type"] == "medication_taken"
    assert evento["toma_id"] == str(TOMA_ID)
    assert evento["paciente_id"] == PACIENTE_ID
    assert evento["medicamento_id"] == MEDICAMENTO_ID
    assert evento["recordatorio_id"] == RECORDATORIO_ID
    assert evento["fecha_programada"] == "2026-04-12 08:00:00"
    assert evento["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert evento["estado"] == "a_tiempo"
    assert evento["diferencia_minutos"] == 3.0
    assert evento["observaciones"] == "Prueba automatizada"


# =========================
# VALIDACIONES DE CAMPOS OBLIGATORIOS
# =========================

def test_paciente_id_obligatorio(colecciones_mock):
    data = datos_validos()
    data["paciente_id"] = None

    with pytest.raises(ValueError, match="paciente_id"):
        TomaService().registrar_toma(**data)


def test_medicamento_id_obligatorio(colecciones_mock):
    data = datos_validos()
    data["medicamento_id"] = ""

    with pytest.raises(ValueError, match="medicamento_id"):
        TomaService().registrar_toma(**data)


def test_recordatorio_id_obligatorio(colecciones_mock):
    data = datos_validos()
    data["recordatorio_id"] = ""

    with pytest.raises(ValueError, match="recordatorio_id"):
        TomaService().registrar_toma(**data)


def test_fecha_programada_obligatoria(colecciones_mock):
    data = datos_validos()
    data["fecha_programada"] = "   "

    with pytest.raises(ValueError, match="fecha_programada"):
        TomaService().registrar_toma(**data)


def test_fecha_hora_toma_obligatoria(colecciones_mock):
    data = datos_validos()
    data["fecha_hora_toma"] = ""

    with pytest.raises(ValueError, match="fecha_hora_toma"):
        TomaService().registrar_toma(**data)


def test_estado_obligatorio(colecciones_mock):
    data = datos_validos()
    data["estado"] = ""

    with pytest.raises(ValueError, match="estado"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACIONES DE EXISTENCIA
# =========================

def test_paciente_no_existe(colecciones_mock):
    colecciones_mock["pacientes_col"].find_one.return_value = None

    with pytest.raises(LookupError, match="paciente no existe"):
        TomaService().registrar_toma(**datos_validos())


def test_medicamento_no_existe(colecciones_mock):
    colecciones_mock["medicamentos_col"].find_one.return_value = None

    with pytest.raises(LookupError, match="medicamento no existe"):
        TomaService().registrar_toma(**datos_validos())


def test_recordatorio_no_existe(colecciones_mock):
    colecciones_mock["recordatorios_col"].find_one.return_value = None

    with pytest.raises(LookupError, match="recordatorio no existe"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# VALIDACIONES DE RELACION ENTRE ENTIDADES
# =========================

def test_medicamento_no_pertenece_al_paciente(colecciones_mock):
    colecciones_mock["medicamentos_col"].find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "paciente_id": "69feaac76a52afc46ed40c99"
    }

    with pytest.raises(ValueError, match="no pertenece al paciente"):
        TomaService().registrar_toma(**datos_validos())


def test_recordatorio_no_pertenece_al_medicamento(colecciones_mock):
    colecciones_mock["recordatorios_col"].find_one.return_value = {
        "_id": ObjectId(RECORDATORIO_ID),
        "medicamento_id": "69feb355322be070cd1c9999"
    }

    with pytest.raises(ValueError, match="no pertenece al medicamento"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# VALIDACION DE DUPLICADOS
# =========================

def test_toma_duplicada_lanza_error(colecciones_mock, monkeypatch):
    monkeypatch.setattr(toma_service_module, "publisher", None)

    colecciones_mock["tomas_col"].find_one.return_value = {
        "_id": TOMA_ID,
        "recordatorio_id": RECORDATORIO_ID,
        "fecha_programada": "2026-04-12 08:00:00"
    }

    with pytest.raises(FileExistsError, match="Ya existe una toma"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# ERROR DE BASE DE DATOS / INSERCIÓN
# =========================

def test_error_insertar_toma_lanza_runtime_error(colecciones_mock):
    colecciones_mock["tomas_col"].find_one.return_value = None
    colecciones_mock["tomas_col"].insert_one.side_effect = Exception("Error simulado MongoDB")

    with pytest.raises(Exception, match="Error simulado MongoDB"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# CONSULTAS
# =========================

def test_obtener_tomas_del_dia(colecciones_mock):
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [
        {
            "_id": TOMA_ID,
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": RECORDATORIO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
            "estado": "a_tiempo",
            "diferencia_minutos": 3.0,
            "observaciones": "Prueba automatizada"
        }
    ]

    colecciones_mock["tomas_col"].find.return_value = cursor_mock

    resultado = TomaService().obtener_tomas_del_dia(PACIENTE_ID, "2026-04-12")

    assert len(resultado) == 1
    assert resultado[0]["id"] == str(TOMA_ID)
    assert resultado[0]["paciente_id"] == PACIENTE_ID


def test_obtener_historial(colecciones_mock):
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [
        {
            "_id": TOMA_ID,
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": RECORDATORIO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
            "estado": "a_tiempo",
            "diferencia_minutos": 3.0,
            "observaciones": "Prueba automatizada"
        }
    ]

    colecciones_mock["tomas_col"].find.return_value = cursor_mock

    resultado = TomaService().obtener_historial(PACIENTE_ID)

    assert len(resultado) == 1
    assert resultado[0]["id"] == str(TOMA_ID)
    assert resultado[0]["paciente_id"] == PACIENTE_ID
    assert resultado[0]["medicamento_id"] == MEDICAMENTO_ID
    assert resultado[0]["estado"] == "tomado"



