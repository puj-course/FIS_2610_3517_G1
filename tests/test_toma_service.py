########################################################################################
#   test_toma_service.py
########################################################################################

import sqlite3
from unittest.mock import Mock

import pytest

from backend.services import toma_service as toma_service_module
from backend.services.toma_service import TomaService


# =========================
# FIXTURES Y DATOS BASE
# =========================

@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "test_toma_service.db"

    monkeypatch.setattr(toma_service_module, "DB_PATH", str(path))

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL
        );

        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            paciente_id INTEGER NOT NULL
        );

        CREATE TABLE recordatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL
        );

        CREATE TABLE historial_tomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medicamento_id INTEGER NOT NULL,
            recordatorio_id INTEGER NOT NULL,
            fecha_programada TEXT NOT NULL,
            fecha_hora_toma TEXT,
            diferencia_minutos REAL,
            estado TEXT NOT NULL,
            observaciones TEXT,
            UNIQUE(recordatorio_id, fecha_programada)
        );
    """)

    # Paciente válido con id = 1
    cursor.execute("""
        INSERT INTO pacientes (nombres)
        VALUES (?)
    """, ("Paciente prueba",))

    # Medicamento válido del paciente 1 con id = 1
    cursor.execute("""
        INSERT INTO medicamentos (nombre, paciente_id)
        VALUES (?, ?)
    """, ("Aspirina", 1))

    # Medicamento de otro paciente con id = 2
    cursor.execute("""
        INSERT INTO medicamentos (nombre, paciente_id)
        VALUES (?, ?)
    """, ("Ibuprofeno", 99))

    # Recordatorio válido del medicamento 1 con id = 1
    cursor.execute("""
        INSERT INTO recordatorios (medicamento_id)
        VALUES (?)
    """, (1,))

    # Recordatorio de otro medicamento con id = 2
    cursor.execute("""
        INSERT INTO recordatorios (medicamento_id)
        VALUES (?)
    """, (2,))

    conn.commit()
    conn.close()

    return path


def datos_validos():
    return {
        "paciente_id": 1,
        "medicamento_id": 1,
        "recordatorio_id": 1,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba automatizada",
    }


# =========================
# REGISTRO EXITOSO
# =========================

def test_registrar_toma_exitoso(db_path, monkeypatch):
    publisher_falso = Mock()
    monkeypatch.setattr(toma_service_module, "publisher", publisher_falso)

    resultado = TomaService().registrar_toma(**datos_validos())

    assert resultado["ok"] is True
    assert resultado["mensaje"] == "Toma registrada correctamente"
    assert resultado["toma_id"] == 1

    assert resultado["data"]["paciente_id"] == 1
    assert resultado["data"]["medicamento_id"] == 1
    assert resultado["data"]["recordatorio_id"] == 1
    assert resultado["data"]["fecha_programada"] == "2026-04-12 08:00:00"
    assert resultado["data"]["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert resultado["data"]["estado"] == "a_tiempo"
    assert resultado["data"]["diferencia_minutos"] == 3.0
    assert resultado["data"]["observaciones"] == "Prueba automatizada"

    publisher_falso.notify.assert_called_once()

    evento = publisher_falso.notify.call_args.args[0]

    assert evento["type"] == "medication_taken"
    assert evento["toma_id"] == 1
    assert evento["paciente_id"] == 1
    assert evento["medicamento_id"] == 1
    assert evento["recordatorio_id"] == 1
    assert evento["fecha_programada"] == "2026-04-12 08:00:00"
    assert evento["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert evento["estado"] == "a_tiempo"
    assert evento["diferencia_minutos"] == 3.0
    assert evento["observaciones"] == "Prueba automatizada"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM historial_tomas WHERE id = ?", (1,))
    toma = cursor.fetchone()

    conn.close()

    assert toma is not None
    assert toma["paciente_id"] == 1
    assert toma["medicamento_id"] == 1
    assert toma["recordatorio_id"] == 1
    assert toma["fecha_programada"] == "2026-04-12 08:00:00"
    assert toma["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert toma["estado"] == "a_tiempo"
    assert toma["diferencia_minutos"] == 3.0
    assert toma["observaciones"] == "Prueba automatizada"


# =========================
# VALIDACIONES DE CAMPOS OBLIGATORIOS
# =========================

def test_paciente_id_obligatorio(db_path):
    data = datos_validos()
    data["paciente_id"] = None

    with pytest.raises(ValueError, match="paciente_id"):
        TomaService().registrar_toma(**data)


def test_medicamento_id_obligatorio(db_path):
    data = datos_validos()
    data["medicamento_id"] = 0

    with pytest.raises(ValueError, match="medicamento_id"):
        TomaService().registrar_toma(**data)


def test_recordatorio_id_obligatorio(db_path):
    data = datos_validos()
    data["recordatorio_id"] = ""

    with pytest.raises(ValueError, match="recordatorio_id"):
        TomaService().registrar_toma(**data)


def test_fecha_programada_obligatoria(db_path):
    data = datos_validos()
    data["fecha_programada"] = "   "

    with pytest.raises(ValueError, match="fecha_programada"):
        TomaService().registrar_toma(**data)


def test_fecha_hora_toma_obligatoria(db_path):
    data = datos_validos()
    data["fecha_hora_toma"] = ""

    with pytest.raises(ValueError, match="fecha_hora_toma"):
        TomaService().registrar_toma(**data)


def test_estado_obligatorio(db_path):
    data = datos_validos()
    data["estado"] = ""

    with pytest.raises(ValueError, match="estado"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACIONES DE EXISTENCIA
# =========================

def test_paciente_no_existe(db_path):
    data = datos_validos()
    data["paciente_id"] = 999

    with pytest.raises(LookupError, match="paciente no existe"):
        TomaService().registrar_toma(**data)


def test_medicamento_no_existe(db_path):
    data = datos_validos()
    data["medicamento_id"] = 999

    with pytest.raises(LookupError, match="medicamento no existe"):
        TomaService().registrar_toma(**data)


def test_recordatorio_no_existe(db_path):
    data = datos_validos()
    data["recordatorio_id"] = 999

    with pytest.raises(LookupError, match="recordatorio no existe"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACIONES DE RELACION ENTRE ENTIDADES
# =========================

def test_medicamento_no_pertenece_al_paciente(db_path):
    data = datos_validos()
    data["medicamento_id"] = 2

    with pytest.raises(ValueError, match="no pertenece al paciente"):
        TomaService().registrar_toma(**data)


def test_recordatorio_no_pertenece_al_medicamento(db_path):
    data = datos_validos()
    data["recordatorio_id"] = 2

    with pytest.raises(ValueError, match="no pertenece al medicamento"):
        TomaService().registrar_toma(**data)


# =========================
# VALIDACION DE DUPLICADOS
# =========================

def test_toma_duplicada_lanza_error(db_path, monkeypatch):
    monkeypatch.setattr(toma_service_module, "publisher", None)

    service = TomaService()

    service.registrar_toma(**datos_validos())

    with pytest.raises(FileExistsError, match="Ya existe una toma"):
        service.registrar_toma(**datos_validos())


# =========================
# ERRORES DE BASE DE DATOS
# =========================

def test_error_base_datos_lanza_runtime_error(tmp_path, monkeypatch):
    ruta_invalida = tmp_path / "carpeta_inexistente" / "database.db"

    monkeypatch.setattr(toma_service_module, "DB_PATH", str(ruta_invalida))

    with pytest.raises(RuntimeError, match="Error de base de datos"):
        TomaService().registrar_toma(**datos_validos())



