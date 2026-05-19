from __future__ import annotations

import copy
import time

from backend.quality_metrics import (
    calcular_cumplimiento_reglas_negocio,
    calcular_rendimiento_latencia,
    construir_reporte_metricas,
)


def escenario_valido():
    return {
        "pacientes": [
            {
                "id": "pac-1",
                "paciente_id": "pac-1",
                "nombres": "Ana",
                "numero_documento": "100200300",
            }
        ],
        "medicamentos": [
            {
                "id": "med-1",
                "medicamento_id": "med-1",
                "nombre": "Losartan",
                "dosis": "50 mg",
                "frecuencia": "Diaria",
                "paciente_id": "pac-1",
            }
        ],
        "recordatorios": [
            {
                "id": "rec-1",
                "recordatorio_id": "rec-1",
                "paciente_id": "pac-1",
                "medicamento_id": "med-1",
                "hora_programada": "08:00",
                "frecuencia": "Diaria",
            }
        ],
        "tomas": [
            {
                "id": "toma-1",
                "toma_id": "toma-1",
                "paciente_id": "pac-1",
                "medicamento_id": "med-1",
                "recordatorio_id": "rec-1",
                "estado": "tomada",
            }
        ],
    }


def construir(payload):
    return construir_reporte_metricas(
        pacientes=payload["pacientes"],
        medicamentos=payload["medicamentos"],
        recordatorios=payload["recordatorios"],
        tomas=payload["tomas"],
    )


def test_escenario_valido_devuelve_porcentajes_y_quality_gate_aprobado():
    reporte = construir(escenario_valido())
    metricas = reporte["resumen_metricas"]

    assert reporte["quality_gate_aprobado"] is True
    assert reporte["estado_general"] == "Aprobado"
    assert metricas["completitud_datos"]["porcentaje"] == 100.0
    assert metricas["cumplimiento_reglas_negocio"]["porcentaje"] == 100.0
    assert metricas["rendimiento_latencia"]["porcentaje"] == 100.0
    assert metricas["rendimiento_latencia"]["nivel"] == "Bueno"

    for metrica in metricas.values():
        assert "porcentaje" in metrica
        assert metrica["lectura"].endswith(metrica["nivel"])


def test_escenario_invalido_por_campos_faltantes_baja_completitud_y_falla_gate():
    payload = escenario_valido()
    payload["pacientes"][0]["nombres"] = ""
    payload["medicamentos"][0]["nombre"] = ""
    payload["medicamentos"][0]["dosis"] = ""
    payload["recordatorios"][0]["hora_programada"] = ""
    payload["recordatorios"][0]["frecuencia"] = ""

    reporte = construir(payload)
    completitud = reporte["resumen_metricas"]["completitud_datos"]

    assert completitud["porcentaje"] < 70
    assert completitud["nivel"] == "Deficiente"
    assert reporte["quality_gate_aprobado"] is False
    assert "completitud_datos" in reporte["notificacion"]["metricas_afectadas"]


def test_escenario_invalido_por_ids_incoherentes_baja_reglas_y_falla_gate():
    payload = escenario_valido()
    payload["recordatorios"][0]["paciente_id"] = "m1"
    payload["recordatorios"][0]["medicamento_id"] = "0"
    payload["tomas"][0]["paciente_id"] = "pac-2"

    reporte = construir(payload)
    reglas = reporte["resumen_metricas"]["cumplimiento_reglas_negocio"]

    assert reglas["porcentaje"] < 70
    assert reglas["nivel"] == "Deficiente"
    assert reglas["reglas_incumplidas"] > 0
    assert reporte["quality_gate_aprobado"] is False
    assert "cumplimiento_reglas_negocio" in reporte["notificacion"]["metricas_afectadas"]
    assert any(
        "Recordatorio asociado a medicamento existente" == regla["regla"]
        for regla in reglas["reglas_fallidas"]
    )


def test_cambiar_un_dato_modifica_el_porcentaje_de_reglas_de_negocio():
    valido = construir(escenario_valido())
    invalido_payload = copy.deepcopy(escenario_valido())
    invalido_payload["recordatorios"][0]["paciente_id"] = "paciente-inexistente"
    invalido = construir(invalido_payload)

    porcentaje_valido = valido["resumen_metricas"]["cumplimiento_reglas_negocio"]["porcentaje"]
    porcentaje_invalido = invalido["resumen_metricas"]["cumplimiento_reglas_negocio"]["porcentaje"]

    assert porcentaje_valido == 100.0
    assert porcentaje_invalido < porcentaje_valido


def test_calcular_cumplimiento_reglas_negocio_valida_relaciones_reales():
    payload = escenario_valido()
    payload["tomas"][0]["medicamento_id"] = "0"

    resultado = calcular_cumplimiento_reglas_negocio(
        payload["pacientes"],
        payload["medicamentos"],
        payload["recordatorios"],
        payload["tomas"],
    )

    assert resultado["porcentaje"] < 100
    assert any(
        regla["regla"] == "Toma asociada a medicamento existente"
        and regla["cumple"] is False
        for regla in resultado["detalle"]
    )


def test_latencia_devuelve_porcentaje_ms_objetivo_y_nivel():
    def operacion_lenta():
        time.sleep(0.02)
        return "ok"

    resultado = calcular_rendimiento_latencia(
        operacion_lenta,
        objetivo_ms=1,
    )

    assert resultado["porcentaje"] < 100
    assert resultado["latencia_ms"] >= 1
    assert resultado["objetivo_ms"] == 1
    assert resultado["nivel"] in {"Bueno", "Aceptable", "Deficiente"}
    assert resultado["resultado"] == "ok"


def test_quality_gate_falla_si_latencia_supera_objetivo():
    payload = escenario_valido()
    payload["tomas"] = [
        {
            "id": f"toma-{indice}",
            "toma_id": f"toma-{indice}",
            "paciente_id": "pac-1",
            "medicamento_id": "med-1",
            "recordatorio_id": "rec-1",
            "estado": "tomada",
        }
        for indice in range(300)
    ]

    reporte = construir_reporte_metricas(
        pacientes=payload["pacientes"],
        medicamentos=payload["medicamentos"],
        recordatorios=payload["recordatorios"],
        tomas=payload["tomas"],
        objetivo_ms=0.001,
    )
    rendimiento = reporte["resumen_metricas"]["rendimiento_latencia"]

    assert rendimiento["porcentaje"] < 70
    assert rendimiento["nivel"] == "Deficiente"
    assert reporte["quality_gate_aprobado"] is False
    assert "rendimiento_latencia" in reporte["notificacion"]["metricas_afectadas"]
