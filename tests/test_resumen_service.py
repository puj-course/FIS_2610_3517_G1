########################################################################################
#   test_resumen_service.py
########################################################################################

import sqlite3

import pytest

from backend.services import resumen_paciente_service as resumen_module
from backend.services.resumen_paciente_service import ResumenPacienteService


# =========================
# FIXTURE DE BASE DE DATOS
# =========================

@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "test_resumen_service.db"

    def get_test_conn():
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(resumen_module, "get_connection", get_test_conn)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            tipo_documento TEXT,
            numero_documento TEXT,
            telefono_contacto TEXT,
            eps_aseguradora TEXT,
            diagnostico_principal TEXT
        );

        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT,
            frecuencia TEXT,
            horario TEXT,
            fecha_inicio TEXT,
            observaciones TEXT,
            paciente_id INTEGER NOT NULL
        );
    """)

    cursor.execute("""
        INSERT INTO pacientes (
            nombres, apellidos, tipo_documento, numero_documento,
            telefono_contacto, eps_aseguradora, diagnostico_principal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Ana",
        "Lopez",
        "CC",
        "12345678",
        "3001234567",
        "Sura",
        "Hipertension",
    ))

    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario,
            fecha_inicio, observaciones, paciente_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Aspirina",
        "500 mg",
        "Cada 8 horas",
        "08:00",
        "2026-04-01",
        "Con comida",
        1,
    ))

    conn.commit()
    conn.close()

    return path


@pytest.fixture
def historial_mock(monkeypatch):
    tomas = [
        {
            "id": 1,
            "paciente_id": 1,
            "medicamento_id": 1,
            "nombre": "Aspirina",
            "fecha": "2026-04-12",
            "hora_programada": "08:00",
            "hora_tomada": "08:05",
            "estado": "tomado",
            "observaciones": "Tomada correctamente",
        },
        {
            "id": 2,
            "paciente_id": 1,
            "medicamento_id": 1,
            "nombre": "Aspirina",
            "fecha": "2026-04-13",
            "hora_programada": "08:00",
            "hora_tomada": None,
            "estado": "pendiente",
            "observaciones": "Pendiente",
        },
    ]

    monkeypatch.setattr(
        resumen_module,
        "obtener_historial_tomas",
        lambda paciente_id: tomas,
    )

    return tomas


# =========================
# PACIENTE
# =========================

def test_paciente_ok(db_path):
    service = ResumenPacienteService()

    paciente = service.obtener_paciente(1)

    assert paciente["id"] == 1
    assert paciente["nombres"] == "Ana"
    assert paciente["apellidos"] == "Lopez"


def test_paciente_none(db_path):
    service = ResumenPacienteService()

    paciente = service.obtener_paciente(999)

    assert paciente is None


# =========================
# MEDICAMENTOS
# =========================

def test_medicamentos_ok(db_path):
    service = ResumenPacienteService()

    medicamentos = service.obtener_medicamentos_activos(1)

    assert len(medicamentos) == 1
    assert medicamentos[0]["nombre"] == "Aspirina"
    assert medicamentos[0]["paciente_id"] == 1


def test_medicamentos_vacio(db_path):
    service = ResumenPacienteService()

    medicamentos = service.obtener_medicamentos_activos(999)

    assert medicamentos == []


# =========================
# HISTORIAL
# =========================

def test_historial_ok(db_path, historial_mock):
    service = ResumenPacienteService()

    historial = service.obtener_historial_formateado(1)

    assert len(historial) == 2
    assert historial[0]["medicamento"] == "Aspirina"
    assert historial[0]["estado"] == "tomado"
    assert historial[1]["estado"] == "pendiente"


# =========================
# RESUMEN DEL PACIENTE
# =========================

def test_resumen_ok(db_path, historial_mock):
    service = ResumenPacienteService()

    resumen = service.construir_resumen(1)

    assert resumen["paciente"]["id"] == 1
    assert resumen["paciente"]["nombres"] == "Ana"
    assert resumen["paciente"]["apellidos"] == "Lopez"

    assert len(resumen["medicamentos_activos"]) == 1
    assert resumen["medicamentos_activos"][0]["nombre"] == "Aspirina"

    assert len(resumen["historial"]) == 2
    assert resumen["cumplimiento"]["total_tomas"] == 2
    assert resumen["cumplimiento"]["tomas_realizadas"] == 1
    assert resumen["cumplimiento"]["porcentaje"] == 50.0

    assert len(resumen["alertas"]) == 1


def test_resumen_404(db_path):
    service = ResumenPacienteService()

    with pytest.raises(LookupError, match="Paciente no encontrado"):
        service.construir_resumen(999)


def test_resumen_vacio(db_path, monkeypatch):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pacientes (
            nombres, apellidos, tipo_documento, numero_documento,
            telefono_contacto, eps_aseguradora, diagnostico_principal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Carlos",
        "Perez",
        "CC",
        "87654321",
        "3111234567",
        "Nueva EPS",
        "Diabetes",
    ))

    conn.commit()
    conn.close()

    monkeypatch.setattr(
        resumen_module,
        "obtener_historial_tomas",
        lambda paciente_id: [],
    )

    service = ResumenPacienteService()
    resumen = service.construir_resumen(2)

    assert resumen["paciente"]["id"] == 2
    assert resumen["paciente"]["nombres"] == "Carlos"
    assert resumen["medicamentos_activos"] == []
    assert resumen["historial"] == []
    assert resumen["cumplimiento"]["total_tomas"] == 0
    assert resumen["cumplimiento"]["porcentaje"] == 0
    assert resumen["alertas"] == []

