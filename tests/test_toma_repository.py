########################################################################################
#   test_toma_repository.py
########################################################################################

import sqlite3

import pytest

from backend import toma_repository as repo_module
from backend.toma_repository import TomaRepository


# =========================
# FIXTURE DE BASE DE DATOS
# =========================

@pytest.fixture
def db_tomas(tmp_path, monkeypatch):
    path = tmp_path / "test_tomas.db"

    def get_test_conn():
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(repo_module, "get_connection", get_test_conn)

    conn = get_test_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE tomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_programada TEXT NOT NULL,
            hora_tomada TEXT,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            observaciones TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO tomas (
            medicamento_id,
            paciente_id,
            fecha,
            hora_programada,
            hora_tomada,
            estado,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        10,
        1,
        "2026-04-12",
        "08:00",
        "08:05",
        "tomada",
        "Toma inicial",
    ))

    conn.commit()
    conn.close()

    return path


# =========================
# REGISTRAR TOMA
# =========================

def test_registrar_toma(db_tomas):
    repo = TomaRepository()

    toma_id = repo.registrar_toma(
        medicamento_id=10,
        paciente_id=1,
        fecha="2026-04-13",
        hora_programada="08:00",
        hora_tomada="08:04",
        estado="tomada",
        observaciones="Nueva toma",
    )

    assert toma_id == 2


def test_valores_default(db_tomas):
    repo = TomaRepository()

    toma_id = repo.registrar_toma(
        medicamento_id=20,
        paciente_id=2,
        fecha="2026-04-14",
        hora_programada="09:00",
    )

    tomas = repo.obtener_tomas_del_dia(
        paciente_id=2,
        fecha="2026-04-14",
    )

    assert toma_id == 2
    assert len(tomas) == 1
    assert tomas[0]["estado"] == "pendiente"
    assert tomas[0]["hora_tomada"] is None
    assert tomas[0]["observaciones"] is None


# =========================
# CONSULTAR TOMAS
# =========================

def test_tomas_del_dia(db_tomas):
    repo = TomaRepository()

    tomas = repo.obtener_tomas_del_dia(
        paciente_id=1,
        fecha="2026-04-12",
    )

    assert len(tomas) == 1
    assert tomas[0]["medicamento_id"] == 10
    assert tomas[0]["paciente_id"] == 1
    assert tomas[0]["estado"] == "tomada"


def test_tomas_vacio(db_tomas):
    repo = TomaRepository()

    tomas = repo.obtener_tomas_del_dia(
        paciente_id=99,
        fecha="2026-04-12",
    )

    assert tomas == []
