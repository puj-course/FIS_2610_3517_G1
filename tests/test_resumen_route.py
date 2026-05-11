import pytest
from fastapi import HTTPException

from backend.routes import resumen_route


PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"


class ServicioResumenFalso:
    def __init__(self, error=None, resumen=None):
        self.error = error
        self.resumen = resumen

    def construir_resumen(self, paciente_id):
        if self.error:
            raise self.error

        if self.resumen is not None:
            return self.resumen

        return {
            "paciente": {
                "id": paciente_id,
                "nombres": "Ana",
                "apellidos": "Torres"
            },
            "medicamentos_activos": [
                {"id": MEDICAMENTO_ID, "nombre": "Aspirina"}
            ],
            "historial": [
                {
                    "id": "toma-1",
                    "paciente_id": paciente_id,
                    "medicamento_id": MEDICAMENTO_ID,
                    "recordatorio_id": "rec-1",
                    "medicamento": "Aspirina",
                    "medicamento_nombre": "Aspirina",
                    "fecha": "2026-04-12",
                    "hora_programada": "08:00",
                    "hora_tomada": "08:03",
                    "estado": "a_tiempo",
                    "observaciones": "Toma a tiempo",
                },
                {
                    "id": "toma-2",
                    "paciente_id": paciente_id,
                    "medicamento_id": MEDICAMENTO_ID,
                    "recordatorio_id": "rec-2",
                    "medicamento": "Aspirina",
                    "medicamento_nombre": "Aspirina",
                    "fecha": "2026-04-13",
                    "hora_programada": "08:00",
                    "hora_tomada": "08:45",
                    "estado": "tarde",
                    "observaciones": "Toma tarde",
                },
                {
                    "id": "toma-3",
                    "paciente_id": paciente_id,
                    "medicamento_id": MEDICAMENTO_ID,
                    "recordatorio_id": "rec-3",
                    "medicamento": "Aspirina",
                    "medicamento_nombre": "Aspirina",
                    "fecha": "2026-04-14",
                    "hora_programada": "08:00",
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
                    "medicamento": "Aspirina",
                    "fecha": "2026-04-14",
                    "hora_programada": "08:00",
                    "mensaje": "Toma de Aspirina no registrada"
                }
            ],
        }


def test_obtener_resumen_ok(monkeypatch):
    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioResumenFalso()
    )

    respuesta = resumen_route.obtener_resumen(PACIENTE_ID)

    assert respuesta["paciente_id"] == PACIENTE_ID
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
    resumen_sin_historial = {
        "paciente": {
            "id": PACIENTE_ID,
            "nombres": "Ana",
            "apellidos": "Torres"
        },
        "medicamentos_activos": [],
        "historial": [],
        "cumplimiento": {
            "total_tomas": 0,
            "tomas_realizadas": 0,
            "porcentaje": 0,
        },
        "alertas": []
    }

    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioResumenFalso(resumen=resumen_sin_historial)
    )

    respuesta = resumen_route.obtener_resumen(PACIENTE_ID)

    assert respuesta["paciente_id"] == PACIENTE_ID
    assert respuesta["nombre_paciente"] == "Ana Torres"
    assert respuesta["total_medicamentos_activos"] == 0
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
        resumen_route.obtener_resumen("69feaac76a52afc46ed40999")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Paciente no encontrado"


def test_obtener_resumen_error_interno(monkeypatch):
    monkeypatch.setattr(
        resumen_route,
        "service",
        ServicioResumenFalso(error=Exception("Error inesperado"))
    )

    with pytest.raises(HTTPException) as exc_info:
        resumen_route.obtener_resumen(PACIENTE_ID)

    assert exc_info.value.status_code == 500
    assert "Error interno" in exc_info.value.detail
