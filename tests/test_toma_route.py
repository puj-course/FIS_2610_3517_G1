########################################################################################
#   test_toma_route.py
########################################################################################

import pytest
from fastapi import HTTPException

from backend.routes import toma_route


class ServicioTomaFalso:
    def __init__(self, error=None):
        self.error = error
        self.ultima_llamada = None

    def registrar_toma(
        self,
        paciente_id,
        medicamento_id,
        recordatorio_id,
        fecha_programada,
        fecha_hora_toma,
        estado,
        observaciones
    ):
        self.ultima_llamada = {
            "paciente_id": paciente_id,
            "medicamento_id": medicamento_id,
            "recordatorio_id": recordatorio_id,
            "fecha_programada": fecha_programada,
            "fecha_hora_toma": fecha_hora_toma,
            "estado": estado,
            "observaciones": observaciones,
        }

        if self.error:
            raise self.error

        return {
            "ok": True,
            "mensaje": "Toma registrada correctamente",
            "toma_id": 1,
            "data": {
                "paciente_id": paciente_id,
                "medicamento_id": medicamento_id,
                "recordatorio_id": recordatorio_id,
                "fecha_programada": fecha_programada,
                "fecha_hora_toma": fecha_hora_toma,
                "estado": "a_tiempo",
                "diferencia_minutos": 3.0,
                "observaciones": observaciones,
            },
        }


class RepositorioFalso:
    def obtener_tomas_del_dia(self, paciente_id, fecha):
        return [
            {
                "id": 1,
                "paciente_id": paciente_id,
                "fecha": fecha,
                "estado": "a_tiempo",
            }
        ]


def test_registrar_toma_ok_formato_nuevo(monkeypatch):
    servicio = ServicioTomaFalso()

    monkeypatch.setattr(
        toma_route,
        "toma_service",
        servicio
    )

    datos = {
        "paciente_id": 1,
        "medicamento_id": 1,
        "recordatorio_id": 1,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba desde test",
    }

    respuesta = toma_route.registrar_toma(datos)

    assert respuesta["ok"] is True
    assert respuesta["mensaje"] == "Toma registrada correctamente"
    assert respuesta["toma_id"] == 1
    assert respuesta["data"]["estado"] == "a_tiempo"

    assert servicio.ultima_llamada["paciente_id"] == 1
    assert servicio.ultima_llamada["medicamento_id"] == 1
    assert servicio.ultima_llamada["recordatorio_id"] == 1
    assert servicio.ultima_llamada["fecha_programada"] == "2026-04-12 08:00:00"
    assert servicio.ultima_llamada["fecha_hora_toma"] == "2026-04-12 08:03:00"
    assert servicio.ultima_llamada["estado"] == "tomada"
    assert servicio.ultima_llamada["observaciones"] == "Prueba desde test"


def test_registrar_toma_ok_formato_anterior(monkeypatch):
    servicio = ServicioTomaFalso()

    monkeypatch.setattr(
        toma_route,
        "toma_service",
        servicio
    )

    datos = {
        "paciente_id": 1,
        "medicamento_id": 1,
        "recordatorio_id": 1,
        "fecha": "2026-04-12",
        "hora_programada": "08:00:00",
        "hora_tomada": "08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba con formato anterior",
    }

    respuesta = toma_route.registrar_toma(datos)

    assert respuesta["ok"] is True
    assert respuesta["data"]["estado"] == "a_tiempo"

    assert servicio.ultima_llamada["fecha_programada"] == "2026-04-12 08:00:00"
    assert servicio.ultima_llamada["fecha_hora_toma"] == "2026-04-12 08:03:00"


def test_registrar_toma_error_400(monkeypatch):
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=ValueError("Datos inválidos"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({})

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Datos inválidos"


def test_registrar_toma_error_404(monkeypatch):
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=LookupError("El paciente no existe"))
    )

    datos = {
        "paciente_id": 999,
        "medicamento_id": 1,
        "recordatorio_id": 1,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
    }

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma(datos)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "El paciente no existe"


def test_registrar_toma_error_409(monkeypatch):
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=FileExistsError("Ya existe una toma"))
    )

    datos = {
        "paciente_id": 1,
        "medicamento_id": 1,
        "recordatorio_id": 1,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
    }

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma(datos)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Ya existe una toma"


def test_registrar_toma_error_500(monkeypatch):
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=RuntimeError("Error de base de datos"))
    )

    datos = {
        "paciente_id": 1,
        "medicamento_id": 1,
        "recordatorio_id": 1,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
    }

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma(datos)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error de base de datos"


def test_obtener_tomas_del_dia(monkeypatch):
    monkeypatch.setattr(
        toma_route,
        "repositorio",
        RepositorioFalso()
    )

    respuesta = toma_route.obtener_tomas(1, "2026-04-12")

    assert "tomas" in respuesta
    assert len(respuesta["tomas"]) == 1
    assert respuesta["tomas"][0]["paciente_id"] == 1
    assert respuesta["tomas"][0]["fecha"] == "2026-04-12"


def test_obtener_tomas_del_dia_sin_fecha(monkeypatch):
    monkeypatch.setattr(
        toma_route,
        "repositorio",
        RepositorioFalso()
    )

    respuesta = toma_route.obtener_tomas(1)

    assert "tomas" in respuesta
    assert len(respuesta["tomas"]) == 1
    assert respuesta["tomas"][0]["paciente_id"] == 1


class CursorHistorialFalso:
    def __init__(self, filas):
        self.filas = filas
        self.query = None
        self.params = None

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.filas


class ConexionHistorialFalsa:
    def __init__(self, filas):
        self.cursor_falso = CursorHistorialFalso(filas)
        self.cerrada = False

    def cursor(self):
        return self.cursor_falso

    def close(self):
        self.cerrada = True


def test_obtener_historial_sin_registros(monkeypatch):
    conexion = ConexionHistorialFalsa([])

    monkeypatch.setattr(
        toma_route,
        "get_connection",
        lambda: conexion
    )

    respuesta = toma_route.obtener_historial(1)

    assert respuesta["historial"] == []
    assert respuesta["cumplimiento"]["total_tomas"] == 0
    assert respuesta["cumplimiento"]["tomas_realizadas"] == 0
    assert respuesta["cumplimiento"]["porcentaje"] == 0
    assert respuesta["alertas"] == []

    assert conexion.cerrada is True
    assert conexion.cursor_falso.params == (1,)


def test_obtener_historial_con_registros(monkeypatch):
    filas = [
        {
            "id": 1,
            "paciente_id": 1,
            "medicamento_id": 1,
            "medicamento_nombre": "Aspirina",
            "medicamento": "Aspirina",
            "recordatorio_id": 1,
            "fecha": "2026-04-12",
            "hora_programada": "08:00:00",
            "hora_tomada": "08:03:00",
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
            "diferencia_minutos": 3.0,
            "estado": "a_tiempo",
            "observaciones": "Toma registrada a tiempo",
        },
        {
            "id": 2,
            "paciente_id": 1,
            "medicamento_id": 1,
            "medicamento_nombre": "Aspirina",
            "medicamento": "Aspirina",
            "recordatorio_id": 1,
            "fecha": "2026-04-13",
            "hora_programada": "08:00:00",
            "hora_tomada": None,
            "fecha_programada": "2026-04-13 08:00:00",
            "fecha_hora_toma": None,
            "diferencia_minutos": None,
            "estado": "omitida",
            "observaciones": "No se registró la toma",
        },
    ]

    conexion = ConexionHistorialFalsa(filas)

    monkeypatch.setattr(
        toma_route,
        "get_connection",
        lambda: conexion
    )

    respuesta = toma_route.obtener_historial(1)

    assert "historial" in respuesta
    assert "cumplimiento" in respuesta
    assert "alertas" in respuesta

    assert len(respuesta["historial"]) == 2
    assert respuesta["cumplimiento"]["total_tomas"] == 2
    assert respuesta["cumplimiento"]["tomas_realizadas"] == 1
    assert respuesta["cumplimiento"]["porcentaje"] == 50.0

    assert conexion.cerrada is True
    assert conexion.cursor_falso.params == (1,)
