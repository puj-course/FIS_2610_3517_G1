import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alertas import strategies as strategies_module
from backend.alertas.strategies import (
    AlertaContext,
    MedicamentoDuplicadoStrategy,
    DosisDuplicadaStrategy,
    RecordatorioSeguimientoStrategy
)


PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"


def test_medicamento_duplicado_strategy_devuelve_alerta(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    medicamentos_col_falsa.find_one.return_value = {
        "_id": MEDICAMENTO_ID,
        "nombre": "acetaminofen",
        "dosis": "500 mg",
        "paciente_id": PACIENTE_ID
    }

    monkeypatch.setattr(
        strategies_module,
        "medicamentos_col",
        medicamentos_col_falsa
    )

    data = {
        "nombre": "Acetaminofen",
        "dosis": "500 mg",
        "paciente_id": PACIENTE_ID
    }

    context = AlertaContext()
    context.set_strategy(MedicamentoDuplicadoStrategy())

    alerta = context.ejecutar(data)

    assert alerta is not None
    assert alerta["tipo"] == "medicamento_duplicado"


def test_medicamento_duplicado_strategy_devuelve_none(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    medicamentos_col_falsa.find_one.return_value = None

    monkeypatch.setattr(
        strategies_module,
        "medicamentos_col",
        medicamentos_col_falsa
    )

    data = {
        "nombre": "Ibuprofeno",
        "dosis": "400 mg",
        "paciente_id": PACIENTE_ID
    }

    context = AlertaContext()
    context.set_strategy(MedicamentoDuplicadoStrategy())

    alerta = context.ejecutar(data)

    assert alerta is None


def test_medicamento_duplicado_strategy_acepta_nombre_medicamento(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    medicamentos_col_falsa.find_one.return_value = {
        "_id": MEDICAMENTO_ID,
        "nombre": "acetaminofen",
        "paciente_id": PACIENTE_ID
    }

    monkeypatch.setattr(
        strategies_module,
        "medicamentos_col",
        medicamentos_col_falsa
    )

    data = {
        "nombre_medicamento": "Acetaminofen",
        "paciente_id": PACIENTE_ID
    }

    context = AlertaContext()
    context.set_strategy(MedicamentoDuplicadoStrategy())

    alerta = context.ejecutar(data)

    assert alerta is not None
    assert alerta["tipo"] == "medicamento_duplicado"


def test_dosis_duplicada_strategy_devuelve_alerta(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    medicamentos_col_falsa.find_one.return_value = {
        "_id": MEDICAMENTO_ID,
        "nombre": "losartan",
        "dosis": "50 mg",
        "paciente_id": PACIENTE_ID
    }

    monkeypatch.setattr(
        strategies_module,
        "medicamentos_col",
        medicamentos_col_falsa
    )

    data = {
        "nombre": "Amlodipino",
        "dosis": "50 mg",
        "paciente_id": PACIENTE_ID
    }

    context = AlertaContext()
    context.set_strategy(DosisDuplicadaStrategy())

    alerta = context.ejecutar(data)

    assert alerta is not None
    assert alerta["tipo"] == "dosis_duplicada"


def test_dosis_duplicada_strategy_devuelve_none(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    medicamentos_col_falsa.find_one.return_value = None

    monkeypatch.setattr(
        strategies_module,
        "medicamentos_col",
        medicamentos_col_falsa
    )

    data = {
        "nombre": "Amlodipino",
        "dosis": "25 mg",
        "paciente_id": PACIENTE_ID
    }

    context = AlertaContext()
    context.set_strategy(DosisDuplicadaStrategy())

    alerta = context.ejecutar(data)

    assert alerta is None


def test_recordatorio_seguimiento_strategy_devuelve_alerta():
    data = {
        "medicamento_id": MEDICAMENTO_ID,
        "activo": 1
    }

    context = AlertaContext()
    context.set_strategy(RecordatorioSeguimientoStrategy())

    alerta = context.ejecutar(data)

    assert alerta is not None
    assert alerta["tipo"] == "seguimiento_recordatorio"


def test_recordatorio_seguimiento_strategy_devuelve_none():
    data = {
        "medicamento_id": MEDICAMENTO_ID,
        "activo": 0
    }

    context = AlertaContext()
    context.set_strategy(RecordatorioSeguimientoStrategy())

    alerta = context.ejecutar(data)

    assert alerta is None