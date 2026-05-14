########################################################################################
# test_toma_service.py
# Pruebas para TomaService usando MongoDB mockeado
########################################################################################

import os
from unittest.mock import Mock, MagicMock

import pytest
from bson import ObjectId

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/medtrack_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-medtrack")

from backend.services import toma_service as toma_service_module
from backend.services.toma_service import TomaService


PACIENTE_ID    = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
TOMA_ID        = ObjectId("69feb500322be070cd1c97d0")


def datos_validos():
    return {
        "paciente_id":     PACIENTE_ID,
        "medicamento_id":  MEDICAMENTO_ID,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma":  "2026-04-12 08:03:00",
        "estado":           "tomada",
        "observaciones":    "Prueba automatizada",
    }


@pytest.fixture
def colecciones_mock(monkeypatch):
    pacientes_col    = MagicMock()
    medicamentos_col = MagicMock()
    tomas_col        = MagicMock()

    pacientes_col.find_one.return_value = {
        "_id":    ObjectId(PACIENTE_ID),
        "nombres": "Paciente prueba"
    }

    medicamentos_col.find_one.return_value = {
        "_id":        ObjectId(MEDICAMENTO_ID),
        "paciente_id": PACIENTE_ID,
        "nombre":      "Aspirina"
    }

    tomas_col.find_one.return_value = None

    insert_result = MagicMock()
    insert_result.inserted_id = TOMA_ID
    tomas_col.insert_one.return_value = insert_result

    monkeypatch.setattr(toma_service_module, "pacientes_col",    pacientes_col)
    monkeypatch.setattr(toma_service_module, "medicamentos_col", medicamentos_col)
    monkeypatch.setattr(toma_service_module, "tomas_col",        tomas_col)
    monkeypatch.setattr(toma_service_module, "publisher",        None)

    return {
        "pacientes_col":    pacientes_col,
        "medicamentos_col": medicamentos_col,
        "tomas_col":        tomas_col,
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

    colecciones_mock["tomas_col"].insert_one.assert_called_once()
    publisher_falso.notify.assert_called_once()

    evento = publisher_falso.notify.call_args.args[0]
    assert evento["type"] == "medication_taken"
    assert evento["toma_id"] == str(TOMA_ID)


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

    with pytest.raises(LookupError, match="paciente"):
        TomaService().registrar_toma(**datos_validos())


def test_medicamento_no_existe(colecciones_mock):
    colecciones_mock["medicamentos_col"].find_one.return_value = None

    with pytest.raises(LookupError, match="medicamento"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# VALIDACIÓN RELACIÓN MEDICAMENTO-PACIENTE
# =========================

def test_medicamento_no_pertenece_al_paciente(colecciones_mock):
    colecciones_mock["medicamentos_col"].find_one.return_value = {
        "_id":        ObjectId(MEDICAMENTO_ID),
        "paciente_id": "69feaac76a52afc46ed40c99"  # paciente diferente
    }

    with pytest.raises(ValueError, match="no pertenece al paciente"):
        TomaService().registrar_toma(**datos_validos())


# =========================
# ERROR DE INSERCIÓN
# =========================

def test_error_insertar_toma_lanza_excepcion(colecciones_mock):
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
            "_id":            TOMA_ID,
            "paciente_id":    PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma":  "2026-04-12 08:03:00",
            "estado":           "a_tiempo",
            "diferencia_minutos": 3.0,
            "observaciones":    "Prueba"
        }
    ]

    colecciones_mock["tomas_col"].find.return_value = cursor_mock

    resultado = TomaService().obtener_tomas_del_dia(PACIENTE_ID, "2026-04-12")

    assert len(resultado) == 1
    assert resultado[0]["paciente_id"] == PACIENTE_ID


def test_obtener_historial(colecciones_mock):
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [
        {
            "_id":            TOMA_ID,
            "paciente_id":    PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma":  "2026-04-12 08:03:00",
            "estado":           "a_tiempo",
            "diferencia_minutos": 3.0,
            "observaciones":    "Prueba"
        }
    ]

    colecciones_mock["tomas_col"].find.return_value = cursor_mock

    resultado = TomaService().obtener_historial(PACIENTE_ID)

    assert len(resultado) == 1
    assert resultado[0]["paciente_id"] == PACIENTE_ID