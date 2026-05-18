from __future__ import annotations

from bson import ObjectId

from backend.routes import quality_metrics_route


class ColeccionFalsa:
    def __init__(self, documentos):
        self.documentos = documentos

    def find(self, filtro):
        assert filtro == {}
        return list(self.documentos)


def payload_valido():
    return {
        "objetivo_ms": 300,
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


def test_post_evaluar_escenario_valido_devuelve_formato_requerido():
    respuesta = quality_metrics_route.evaluar_metricas_calidad(payload_valido())
    metricas = respuesta["resumen_metricas"]

    assert respuesta["quality_gate_aprobado"] is True
    assert respuesta["estado_general"] == "Aprobado"
    assert respuesta["notificacion"]["tipo"] == "APROBADO"
    assert metricas["completitud_datos"]["porcentaje"] == 100.0
    assert metricas["cumplimiento_reglas_negocio"]["porcentaje"] == 100.0
    assert metricas["rendimiento_latencia"]["porcentaje"] == 100.0


def test_post_evaluar_escenario_invalido_muestra_reglas_fallidas():
    payload = payload_valido()
    payload["recordatorios"][0]["paciente_id"] = "m1"
    payload["recordatorios"][0]["medicamento_id"] = "0"
    payload["tomas"][0]["paciente_id"] = "pac-2"

    respuesta = quality_metrics_route.evaluar_metricas_calidad(payload)
    reglas = respuesta["resumen_metricas"]["cumplimiento_reglas_negocio"]

    assert respuesta["quality_gate_aprobado"] is False
    assert respuesta["notificacion"]["tipo"] == "REQUIERE_MEJORA"
    assert reglas["porcentaje"] < 70
    assert len(reglas["reglas_fallidas"]) > 0


def test_get_resumen_lee_mongo_y_serializa_object_id(monkeypatch):
    paciente_id = ObjectId()
    medicamento_id = ObjectId()
    recordatorio_id = ObjectId()
    toma_id = ObjectId()

    monkeypatch.setattr(
        quality_metrics_route,
        "pacientes_col",
        ColeccionFalsa([
            {
                "_id": paciente_id,
                "nombres": "Ana",
                "numero_documento": "100200300",
            }
        ]),
    )
    monkeypatch.setattr(
        quality_metrics_route,
        "medicamentos_col",
        ColeccionFalsa([
            {
                "_id": medicamento_id,
                "nombre": "Losartan",
                "dosis": "50 mg",
                "frecuencia": "Diaria",
                "paciente_id": str(paciente_id),
            }
        ]),
    )
    monkeypatch.setattr(
        quality_metrics_route,
        "recordatorios_col",
        ColeccionFalsa([
            {
                "_id": recordatorio_id,
                "paciente_id": str(paciente_id),
                "medicamento_id": str(medicamento_id),
                "hora_recordatorio": "08:00",
                "frecuencia": "Diaria",
            }
        ]),
    )
    monkeypatch.setattr(
        quality_metrics_route,
        "tomas_col",
        ColeccionFalsa([
            {
                "_id": toma_id,
                "paciente_id": str(paciente_id),
                "medicamento_id": str(medicamento_id),
                "recordatorio_id": str(recordatorio_id),
            }
        ]),
    )

    respuesta = quality_metrics_route.obtener_metricas_calidad()

    assert respuesta["quality_gate_aprobado"] is True
    assert respuesta["resumen_metricas"]["completitud_datos"]["porcentaje"] == 100.0
    assert respuesta["resumen_metricas"]["cumplimiento_reglas_negocio"]["porcentaje"] == 100.0


def test_post_evaluar_sin_detalle_oculta_detalle_pesado():
    respuesta = quality_metrics_route.evaluar_metricas_calidad(
        payload_valido(),
        incluir_detalle=False,
    )
    reglas = respuesta["resumen_metricas"]["cumplimiento_reglas_negocio"]

    assert "detalle" not in reglas
    assert "reglas_fallidas" not in reglas
