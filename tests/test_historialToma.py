########################################################################################
#   test_historialToma.py
########################################################################################

import pytest

from backend.historial_toma import HistorialToma, HistorialTomaBuilder


# =========================
# CALCULO DE ESTADO
# =========================

def test_calcular_estado_sin_fecha_hora_toma_es_omitida():
    estado, diferencia = HistorialToma.calcular_estado(
        "2026-04-12 08:00:00",
        None,
    )

    assert estado == "omitida"
    assert diferencia is None


def test_calcular_estado_con_formato_invalido_es_omitida():
    estado, diferencia = HistorialToma.calcular_estado(
        "2026/04/12 08:00",
        "2026-04-12 08:05:00",
    )

    assert estado == "omitida"
    assert diferencia is None


def test_calcular_estado_a_tiempo():
    estado, diferencia = HistorialToma.calcular_estado(
        "2026-04-12 08:00:00",
        "2026-04-12 08:20:00",
    )

    assert estado == "a_tiempo"
    assert diferencia == 20


def test_calcular_estado_tarde():
    estado, diferencia = HistorialToma.calcular_estado(
        "2026-04-12 08:00:00",
        "2026-04-12 09:10:00",
    )

    assert estado == "tarde"
    assert diferencia == 70


# =========================
# BUILDER
# =========================

def test_builder_historial_toma():
    historial = (
        HistorialTomaBuilder()
        .set_paciente(1)
        .set_medicamento(2)
        .set_recordatorio(3)
        .set_fecha_programada("2026-04-12 08:00:00")
        .set_fecha_hora_toma("2026-04-12 08:05:00")
        .set_observaciones("Tomada con agua")
        .build()
    )

    datos = historial.to_dict()

    assert datos["paciente_id"] == 1
    assert datos["medicamento_id"] == 2
    assert datos["recordatorio_id"] == 3
    assert datos["estado"] == "a_tiempo"
    assert datos["diferencia_minutos"] == 5
    assert datos["observaciones"] == "Tomada con agua"


def test_builder_sin_paciente():
    builder = (
        HistorialTomaBuilder()
        .set_medicamento(2)
        .set_fecha_programada("2026-04-12 08:00:00")
    )

    with pytest.raises(ValueError, match="paciente_id"):
        builder.build()


def test_builder_sin_medicamento():
    builder = (
        HistorialTomaBuilder()
        .set_paciente(1)
        .set_fecha_programada("2026-04-12 08:00:00")
    )

    with pytest.raises(ValueError, match="medicamento_id"):
        builder.build()


def test_builder_sin_fecha():
    builder = (
        HistorialTomaBuilder()
        .set_paciente(1)
        .set_medicamento(2)
    )

    with pytest.raises(ValueError, match="fecha_programada"):
        builder.build()
