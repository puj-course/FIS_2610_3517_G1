########################################################################################
#   test_resumen_route.py
########################################################################################

import pytest
from fastapi import HTTPException

from backend.routes import resumen_route


class ServicioResumenFalso:
    def __init__(self, error=None):
        self.error = error

    def construir_resumen(self, paciente_id):
        if self.error:
            raise self.error

        return {
            "paciente": {
                "nombres": "Ana",
                "apellidos": "Torres",
            },
            "medicamentos_activos": [
                {"id": 1, "nombre": "Aspirina"}
            ],
            "historial": [
                {
                    "id": 1,
                    "paciente_id": paciente_id,
                    "medicamento_id": 1,
                    "recordatorio_id": 1,
                    "medicamento": "Aspirina",
                    "medicamento_nombre": "Aspirina",
                    "fecha": "2026-04-12",
                    "hora_programada": "08:00:00",
                    "hora_tomada": "08:03:00",
                    "estado": "a_tiempo",
                    "observaciones": "Prueba de toma a tiempo",
                },
                {
                    "id": 2,
                    "paciente_id": paciente_id,
                    "medicamento_id": 1,
                    "recordatorio_id": 1,
                    "medicamento": "Aspirina",
                    "medicamento_nombre": "Aspirina",
                    "fecha": "2026-04-13",
                    "hora_programada": "08:00:00",
                    "hora_tomada": "08:45:00",
                    "estado": "tarde",
                    "observaciones": "Prueba de toma tarde",
                },
                {
                    "id": 3,
                    "paciente_id": paciente_id,
                    "medicamento_id": 1,
                    "recordatorio_id": 1,
                    "medicamento": "Aspirina",
                    "medicamento_nombre": "Aspirina",
                    "fecha": "2026-04-14",
                    "hora_programada": "08:00:00",
                    "hora_tomada": None,
                    "estado": "omitida",
                    "observaciones": "No se registró la toma",
                },
            ],
            "cumplimiento": {
                "total_tomas": 3,
                "tomas_realizadas": 2,
                "porcentaje": 66.67,
            },
            "alertas": [
                {
                    "tipo": "toma_omitida",
                    "severidad": "media",
                    "mensaje": "Toma de Aspirina no registrada",
                    "fecha_creacion": "2026-04-14",
                }
            ],
        }


def test_obtener_resumen_ok(monkeypatch):
    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioResumenFalso()
    )

    respuesta = resumen_route.obtener_resumen(1)

    assert respuesta["paciente_id"] == 1
    assert respuesta["nombre_paciente"] == "Ana Torres"
    assert respuesta["total_medicamentos_activos"] == 1

    assert respuesta["total_tomas_esperadas"] == 3
    assert respuesta["total_tomas_esperadas_hoy"] == 3

    assert respuesta["tomas_realizadas"] == 2
    assert respuesta["tomas_registradas_hoy"] == 2

    assert respuesta["tomas_a_tiempo"] == 1
    assert respuesta["tomas_tarde"] == 1
    assert respuesta["tomas_omitidas"] == 1
    assert respuesta["tomas_pendientes"] == 0
    assert respuesta["tomas_atrasadas"] == 1

    assert respuesta["porcentaje_cumplimiento"] == 66.67
    assert len(respuesta["alertas_activas"]) == 1
    assert len(respuesta["historial"]) == 3


def test_obtener_resumen_paciente_sin_historial(monkeypatch):
    servicio = ServicioResumenFalso()
    resumen = servicio.construir_resumen(1)

    resumen["historial"] = []
    resumen["cumplimiento"] = {
        "total_tomas": 0,
        "tomas_realizadas": 0,
        "porcentaje": 0,
    }
    resumen["alertas"] = []

    class ServicioSinHistorial:
        def construir_resumen(self, paciente_id):
            return resumen

    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioSinHistorial()
    )

    respuesta = resumen_route.obtener_resumen(1)

    assert respuesta["paciente_id"] == 1
    assert respuesta["total_tomas_esperadas"] == 0
    assert respuesta["tomas_realizadas"] == 0
    assert respuesta["tomas_a_tiempo"] == 0
    assert respuesta["tomas_tarde"] == 0
    assert respuesta["tomas_omitidas"] == 0
    assert respuesta["tomas_pendientes"] == 0
    assert respuesta["tomas_atrasadas"] == 0
    assert respuesta["porcentaje_cumplimiento"] == 0
    assert respuesta["historial"] == []
    assert respuesta["alertas_activas"] == []


def test_obtener_resumen_paciente_no_encontrado(monkeypatch):
    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioResumenFalso(error=LookupError("Paciente no encontrado"))
    )

    with pytest.raises(HTTPException) as exc_info:
        resumen_route.obtener_resumen(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Paciente no encontrado"


def test_obtener_resumen_error_interno(monkeypatch):
    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioResumenFalso(error=Exception("Error inesperado"))
    )

    with pytest.raises(HTTPException) as exc_info:
        resumen_route.obtener_resumen(1)

    assert exc_info.value.status_code == 500
    assert "Error interno" in exc_info.value.detail
