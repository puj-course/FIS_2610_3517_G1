import pytest
from fastapi import HTTPException

from backend.routes import toma_route


PACIENTE_ID    = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
TOMA_ID        = "69fec1110dfd411e13b01ee"


class ServicioTomaFalso:
    """
    Servicio falso que simula TomaService.
    Ya no tiene recordatorio_id porque las tomas no dependen de recordatorios.
    """

    def __init__(self, error=None, historial=None, tomas_dia=None):
        self.error     = error
        self.historial = historial if historial is not None else []
        self.tomas_dia = tomas_dia if tomas_dia is not None else []
        self.ultima_llamada              = None
        self.ultima_consulta_dia         = None
        self.ultima_consulta_historial   = None

    def registrar_toma(
        self,
        paciente_id,
        medicamento_id,
        fecha_programada,
        fecha_hora_toma,
        estado,
        observaciones,
        **kwargs   # absorbe recordatorio_id u otros campos opcionales
    ):
        self.ultima_llamada = {
            "paciente_id":     paciente_id,
            "medicamento_id":  medicamento_id,
            "fecha_programada": fecha_programada,
            "fecha_hora_toma":  fecha_hora_toma,
            "estado":           estado,
            "observaciones":    observaciones,
        }

        if self.error:
            raise self.error

        return {
            "ok":      True,
            "mensaje": "Toma registrada correctamente",
            "toma_id": TOMA_ID,
            "data": {
                "paciente_id":      paciente_id,
                "medicamento_id":   medicamento_id,
                "fecha_programada": fecha_programada,
                "fecha_hora_toma":  fecha_hora_toma,
                "estado":           "a_tiempo",
                "diferencia_minutos": 3.0,
                "observaciones":    observaciones,
            },
        }

    def obtener_tomas_del_dia(self, paciente_id, fecha):
        self.ultima_consulta_dia = {"paciente_id": paciente_id, "fecha": fecha}

        if self.tomas_dia:
            return self.tomas_dia

        return [
            {
                "id":             TOMA_ID,
                "paciente_id":    paciente_id,
                "fecha_programada": f"{fecha} 08:00:00",
                "estado":           "a_tiempo",
            }
        ]

    def obtener_historial(self, paciente_id):
        self.ultima_consulta_historial = {"paciente_id": paciente_id}
        return self.historial


# =========================
# REGISTRO DE TOMA
# =========================

def test_registrar_toma_ok(monkeypatch):
    servicio = ServicioTomaFalso()
    monkeypatch.setattr(toma_route, "toma_service", servicio)

    datos = {
        "paciente_id":      PACIENTE_ID,
        "medicamento_id":   MEDICAMENTO_ID,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma":  "2026-04-12 08:03:00",
        "estado":           "tomada",
        "observaciones":    "Prueba desde test",
    }

    respuesta = toma_route.registrar_toma(datos)

    assert respuesta["ok"] is True
    assert respuesta["toma_id"] == TOMA_ID
    assert servicio.ultima_llamada["paciente_id"]    == PACIENTE_ID
    assert servicio.ultima_llamada["medicamento_id"] == MEDICAMENTO_ID


def test_registrar_toma_error_400(monkeypatch):
    monkeypatch.setattr(
        toma_route, "toma_service",
        ServicioTomaFalso(error=ValueError("Datos inválidos"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({})

    assert exc_info.value.status_code == 400


def test_registrar_toma_error_404(monkeypatch):
    monkeypatch.setattr(
        toma_route, "toma_service",
        ServicioTomaFalso(error=LookupError("Paciente no existe"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({
            "paciente_id":      PACIENTE_ID,
            "medicamento_id":   MEDICAMENTO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma":  "2026-04-12 08:03:00",
        })

    assert exc_info.value.status_code == 404


def test_registrar_toma_error_500(monkeypatch):
    monkeypatch.setattr(
        toma_route, "toma_service",
        ServicioTomaFalso(error=RuntimeError("Error DB"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({
            "paciente_id":      PACIENTE_ID,
            "medicamento_id":   MEDICAMENTO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma":  "2026-04-12 08:03:00",
        })

    assert exc_info.value.status_code == 500


# =========================
# CONSULTA DE TOMAS DEL DÍA
# =========================

def test_obtener_tomas_del_dia(monkeypatch):
    servicio = ServicioTomaFalso(
        tomas_dia=[
            {
                "id":             TOMA_ID,
                "paciente_id":    PACIENTE_ID,
                "fecha_programada": "2026-04-12 08:00:00",
                "estado":           "a_tiempo",
            }
        ]
    )

    monkeypatch.setattr(toma_route, "toma_service", servicio)

    respuesta = toma_route.obtener_tomas(PACIENTE_ID, "2026-04-12")

    assert "tomas" in respuesta
    assert len(respuesta["tomas"]) == 1
    assert respuesta["tomas"][0]["paciente_id"] == PACIENTE_ID
    assert servicio.ultima_consulta_dia["fecha"] == "2026-04-12"


def test_obtener_tomas_del_dia_sin_fecha(monkeypatch):
    servicio = ServicioTomaFalso()
    monkeypatch.setattr(toma_route, "toma_service", servicio)

    respuesta = toma_route.obtener_tomas(PACIENTE_ID)

    assert "tomas" in respuesta
    assert servicio.ultima_consulta_dia["paciente_id"] == PACIENTE_ID


# =========================
# CONSULTA DE HISTORIAL
# =========================

def test_obtener_historial_vacio(monkeypatch):
    servicio = ServicioTomaFalso(historial=[])
    monkeypatch.setattr(toma_route, "toma_service", servicio)

    respuesta = toma_route.obtener_historial(PACIENTE_ID)

    assert respuesta["historial"] == []
    assert respuesta["cumplimiento"]["total_tomas"] == 0
    assert respuesta["alertas"] == []


def test_obtener_historial_con_registros(monkeypatch):
    historial = [
        {
            "id":               "toma-1",
            "paciente_id":      PACIENTE_ID,
            "medicamento_id":   MEDICAMENTO_ID,
            "medicamento_nombre": "Aspirina",
            "medicamento":        "Aspirina",
            "fecha":              "2026-04-12",
            "hora_programada":    "08:00",
            "hora_tomada":        "08:03",
            "fecha_programada":   "2026-04-12 08:00:00",
            "fecha_hora_toma":    "2026-04-12 08:03:00",
            "diferencia_minutos": 3.0,
            "estado":             "tomado",
            "observaciones":      "Ok",
        },
        {
            "id":               "toma-2",
            "paciente_id":      PACIENTE_ID,
            "medicamento_id":   MEDICAMENTO_ID,
            "medicamento_nombre": "Aspirina",
            "medicamento":        "Aspirina",
            "fecha":              "2026-04-13",
            "hora_programada":    "08:00",
            "hora_tomada":        None,
            "fecha_programada":   "2026-04-13 08:00:00",
            "fecha_hora_toma":    None,
            "diferencia_minutos": None,
            "estado":             "omitida",
            "observaciones":      "No registrada",
        },
    ]

    servicio = ServicioTomaFalso(historial=historial)
    monkeypatch.setattr(toma_route, "toma_service", servicio)

    respuesta = toma_route.obtener_historial(PACIENTE_ID)

    assert len(respuesta["historial"]) == 2
    assert respuesta["cumplimiento"]["total_tomas"] == 2
    assert respuesta["cumplimiento"]["tomas_realizadas"] == 1
    assert len(respuesta["alertas"]) == 1