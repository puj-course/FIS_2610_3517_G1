import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alertas.strategies import (
    AlertaContext,
    MedicamentoDuplicadoStrategy,
    DosisDuplicadaStrategy,
    RecordatorioSeguimientoStrategy
)


def crear_tabla_medicamentos(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT NOT NULL,
            frecuencia TEXT NOT NULL,
            horario TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            observaciones TEXT,
            paciente_id INTEGER NOT NULL
        )
    """)
    conn.commit()


def test_medicamento_duplicado_strategy_devuelve_alerta():
    conn = sqlite3.connect(":memory:")
    crear_tabla_medicamentos(conn)

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario, fecha_inicio, observaciones, paciente_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Acetaminofen", "500 mg", "Cada 8 horas", "08:00 AM", "03/28/2026", "", 1
    ))
    conn.commit()

    data = {
        "nombre": "Acetaminofen",
        "dosis": "500 mg",
        "paciente_id": 1
    }

    context = AlertaContext(MedicamentoDuplicadoStrategy())
    alerta = context.ejecutar(data, conn)

    assert alerta is not None
    assert alerta["tipo"] == "medicamento_duplicado"

    conn.close()


def test_medicamento_duplicado_strategy_devuelve_none():
    conn = sqlite3.connect(":memory:")
    crear_tabla_medicamentos(conn)

    data = {
        "nombre": "Ibuprofeno",
        "dosis": "400 mg",
        "paciente_id": 1
    }

    context = AlertaContext(MedicamentoDuplicadoStrategy())
    alerta = context.ejecutar(data, conn)

    assert alerta is None

    conn.close()


def test_dosis_duplicada_strategy_devuelve_alerta():
    conn = sqlite3.connect(":memory:")
    crear_tabla_medicamentos(conn)

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario, fecha_inicio, observaciones, paciente_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Losartan", "50 mg", "Cada 12 horas", "09:00 AM", "03/28/2026", "", 1
    ))
    conn.commit()

    data = {
        "nombre": "Amlodipino",
        "dosis": "50 mg",
        "paciente_id": 1
    }

    context = AlertaContext(DosisDuplicadaStrategy())
    alerta = context.ejecutar(data, conn)

    assert alerta is not None
    assert alerta["tipo"] == "dosis_duplicada"

    conn.close()


def test_recordatorio_seguimiento_strategy_devuelve_alerta():
    data = {
        "medicamento_id": 1,
        "activo": 1
    }

    context = AlertaContext(RecordatorioSeguimientoStrategy())
    alerta = context.ejecutar(data)

    assert alerta is not None
    assert alerta["tipo"] == "seguimiento_recordatorio"


def test_recordatorio_seguimiento_strategy_devuelve_none():
    data = {
        "medicamento_id": 1,
        "activo": 0
    }

    context = AlertaContext(RecordatorioSeguimientoStrategy())
    alerta = context.ejecutar(data)

    assert alerta is None