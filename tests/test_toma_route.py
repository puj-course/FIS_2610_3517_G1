import pytest
from fastapi import HTTPException

from backend.routes import toma_route


PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
RECORDATORIO_ID = "69fec00d0dfd411e13b01ed"
TOMA_ID = "69fec1110dfd411e13b01ee"


# =========================
# SERVICIO FALSO PARA LA RUTA
# =========================

class ServicioTomaFalso:
    """
    Servicio falso para reemplazar toma_route.toma_service durante las pruebas.

    toma_route.py ya no usa repositorio ni get_connection.
    Ahora todas las operaciones pasan por el objeto global:

        toma_service = TomaService()

    Por eso este falso implementa los métodos que usa la ruta:
        - registrar_toma()
        - obtener_tomas_del_dia()
        - obtener_historial()
    """

    def __init__(self, error=None, historial=None, tomas_dia=None):
        self.error = error
        self.historial = historial if historial is not None else []
        self.tomas_dia = tomas_dia if tomas_dia is not None else []
        self.ultima_llamada = None
        self.ultima_consulta_dia = None
        self.ultima_consulta_historial = None

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
        """
        Simula TomaService.registrar_toma().

        Guarda los parámetros recibidos para verificar que la ruta construye
        correctamente fecha_programada y fecha_hora_toma.
        """
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
            "toma_id": TOMA_ID,
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

    def obtener_tomas_del_dia(self, paciente_id, fecha):
        """
        Simula TomaService.obtener_tomas_del_dia().

        La ruta GET /tomas/dia/{paciente_id} debe llamar este método
        y devolver el resultado dentro de {"tomas": ...}.
        """
        self.ultima_consulta_dia = {
            "paciente_id": paciente_id,
            "fecha": fecha
        }

        if self.tomas_dia:
            return self.tomas_dia

        return [
            {
                "id": TOMA_ID,
                "paciente_id": paciente_id,
                "fecha_programada": f"{fecha} 08:00:00",
                "fecha_hora_toma": f"{fecha} 08:03:00",
                "estado": "a_tiempo",
            }
        ]

    def obtener_historial(self, paciente_id):
        """
        Simula TomaService.obtener_historial().

        La ruta GET /tomas/historial/{paciente_id} usa este método.
        Si el historial está vacío, la ruta responde directamente con
        cumplimiento en cero. Si hay registros, aplica los decorators.
        """
        self.ultima_consulta_historial = {
            "paciente_id": paciente_id
        }

        return self.historial


# =========================
# REGISTRO DE TOMA
# =========================

def test_registrar_toma_ok_formato_nuevo(monkeypatch):
    """
    CASO VÁLIDO: registrar toma usando el formato nuevo.

    En este formato ya vienen:
        - fecha_programada
        - fecha_hora_toma

    La ruta debe enviarlas directamente al servicio.
    """
    servicio = ServicioTomaFalso()
    monkeypatch.setattr(toma_route, "toma_service", servicio)

    datos = {
        "paciente_id": PACIENTE_ID,
        "medicamento_id": MEDICAMENTO_ID,
        "recordatorio_id": RECORDATORIO_ID,
        "fecha_programada": "2026-04-12 08:00:00",
        "fecha_hora_toma": "2026-04-12 08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba desde test",
    }

    respuesta = toma_route.registrar_toma(datos)

    assert respuesta["ok"] is True
    assert respuesta["toma_id"] == TOMA_ID
    assert respuesta["data"]["estado"] == "a_tiempo"
    assert servicio.ultima_llamada["paciente_id"] == PACIENTE_ID
    assert servicio.ultima_llamada["medicamento_id"] == MEDICAMENTO_ID
    assert servicio.ultima_llamada["recordatorio_id"] == RECORDATORIO_ID
    assert servicio.ultima_llamada["fecha_programada"] == "2026-04-12 08:00:00"
    assert servicio.ultima_llamada["fecha_hora_toma"] == "2026-04-12 08:03:00"


def test_registrar_toma_ok_formato_anterior(monkeypatch):
    """
    CASO VÁLIDO: registrar toma usando formato anterior.

    En el formato anterior llegan:
        - fecha
        - hora_programada
        - hora_tomada

    La ruta debe convertirlos a:
        - fecha_programada
        - fecha_hora_toma
    """
    servicio = ServicioTomaFalso()
    monkeypatch.setattr(toma_route, "toma_service", servicio)

    datos = {
        "paciente_id": PACIENTE_ID,
        "medicamento_id": MEDICAMENTO_ID,
        "recordatorio_id": RECORDATORIO_ID,
        "fecha": "2026-04-12",
        "hora_programada": "08:00:00",
        "hora_tomada": "08:03:00",
        "estado": "tomada",
        "observaciones": "Prueba con formato anterior",
    }

    respuesta = toma_route.registrar_toma(datos)

    assert respuesta["ok"] is True
    assert servicio.ultima_llamada["fecha_programada"] == "2026-04-12 08:00:00"
    assert servicio.ultima_llamada["fecha_hora_toma"] == "2026-04-12 08:03:00"


def test_registrar_toma_error_400(monkeypatch):
    """
    CASO INVÁLIDO: el servicio lanza ValueError.

    La ruta debe convertirlo en HTTPException 400.
    """
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=ValueError("Datos inválidos"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({})

    assert exc_info.value.status_code == 400


def test_registrar_toma_error_404(monkeypatch):
    """
    CASO INVÁLIDO: el servicio lanza LookupError.

    La ruta debe convertirlo en HTTPException 404.
    """
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=LookupError("El paciente no existe"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": RECORDATORIO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
        })

    assert exc_info.value.status_code == 404


def test_registrar_toma_error_409(monkeypatch):
    """
    CASO INVÁLIDO: el servicio lanza FileExistsError.

    La ruta debe convertirlo en HTTPException 409.
    """
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=FileExistsError("Ya existe una toma"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": RECORDATORIO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
        })

    assert exc_info.value.status_code == 409


def test_registrar_toma_error_500(monkeypatch):
    """
    CASO INVÁLIDO: el servicio lanza RuntimeError.

    La ruta debe convertirlo en HTTPException 500.
    """
    monkeypatch.setattr(
        toma_route,
        "toma_service",
        ServicioTomaFalso(error=RuntimeError("Error de base de datos"))
    )

    with pytest.raises(HTTPException) as exc_info:
        toma_route.registrar_toma({
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": RECORDATORIO_ID,
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
        })

    assert exc_info.value.status_code == 500


# =========================
# CONSULTA DE TOMAS DEL DÍA
# =========================

def test_obtener_tomas_del_dia(monkeypatch):
    """
    CASO VÁLIDO: consultar tomas del día con fecha explícita.

    La ruta debe llamar:
        toma_service.obtener_tomas_del_dia(paciente_id, fecha)

    y devolver:
        {"tomas": ...}
    """
    servicio = ServicioTomaFalso(
        tomas_dia=[
            {
                "id": TOMA_ID,
                "paciente_id": PACIENTE_ID,
                "fecha_programada": "2026-04-12 08:00:00",
                "estado": "a_tiempo",
            }
        ]
    )

    monkeypatch.setattr(
        toma_route,
        "toma_service",
        servicio
    )

    respuesta = toma_route.obtener_tomas(PACIENTE_ID, "2026-04-12")

    assert "tomas" in respuesta
    assert len(respuesta["tomas"]) == 1
    assert respuesta["tomas"][0]["paciente_id"] == PACIENTE_ID
    assert respuesta["tomas"][0]["fecha_programada"] == "2026-04-12 08:00:00"

    assert servicio.ultima_consulta_dia["paciente_id"] == PACIENTE_ID
    assert servicio.ultima_consulta_dia["fecha"] == "2026-04-12"


def test_obtener_tomas_del_dia_sin_fecha(monkeypatch):
    """
    CASO VÁLIDO: consultar tomas del día sin enviar fecha.

    Si fecha no llega, la ruta usa date.today().
    No validamos la fecha exacta para evitar que el test dependa del día real.
    """
    servicio = ServicioTomaFalso()

    monkeypatch.setattr(
        toma_route,
        "toma_service",
        servicio
    )

    respuesta = toma_route.obtener_tomas(PACIENTE_ID)

    assert "tomas" in respuesta
    assert len(respuesta["tomas"]) == 1
    assert respuesta["tomas"][0]["paciente_id"] == PACIENTE_ID

    assert servicio.ultima_consulta_dia["paciente_id"] == PACIENTE_ID
    assert servicio.ultima_consulta_dia["fecha"] is not None


# =========================
# CONSULTA DE HISTORIAL
# =========================

def test_obtener_historial_sin_registros(monkeypatch):
    """
    CASO SIN REGISTROS: el servicio retorna historial vacío.

    La ruta debe responder con:
        historial vacío
        cumplimiento en cero
        alertas vacías
    """
    servicio = ServicioTomaFalso(historial=[])

    monkeypatch.setattr(
        toma_route,
        "toma_service",
        servicio
    )

    respuesta = toma_route.obtener_historial(PACIENTE_ID)

    assert respuesta["historial"] == []
    assert respuesta["cumplimiento"]["total_tomas"] == 0
    assert respuesta["alertas"] == []

    assert servicio.ultima_consulta_historial["paciente_id"] == PACIENTE_ID


def test_obtener_historial_con_registros(monkeypatch):
    """
    CASO VÁLIDO: el servicio retorna historial con registros.

    La ruta debe aplicar:
        HistorialTomas
        CumplimientoDecorator
        AlertasDecorator

    y devolver una estructura con historial, cumplimiento y alertas.
    """
    historial = [
        {
            "id": "toma-1",
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "medicamento_nombre": "Aspirina",
            "medicamento": "Aspirina",
            "recordatorio_id": RECORDATORIO_ID,
            "fecha": "2026-04-12",
            "hora_programada": "08:00",
            "hora_tomada": "08:03",
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:03:00",
            "diferencia_minutos": 3.0,
            "estado": "tomado",
            "observaciones": "Toma registrada a tiempo",
        },
        {
            "id": "toma-2",
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "medicamento_nombre": "Aspirina",
            "medicamento": "Aspirina",
            "recordatorio_id": RECORDATORIO_ID,
            "fecha": "2026-04-13",
            "hora_programada": "08:00",
            "hora_tomada": None,
            "fecha_programada": "2026-04-13 08:00:00",
            "fecha_hora_toma": None,
            "diferencia_minutos": None,
            "estado": "omitida",
            "observaciones": "No se registró la toma",
        },
    ]

    servicio = ServicioTomaFalso(historial=historial)

    monkeypatch.setattr(
        toma_route,
        "toma_service",
        servicio
    )

    respuesta = toma_route.obtener_historial(PACIENTE_ID)

    assert len(respuesta["historial"]) == 2
    assert respuesta["cumplimiento"]["total_tomas"] == 2
    assert respuesta["cumplimiento"]["tomas_realizadas"] == 1
    assert respuesta["cumplimiento"]["porcentaje"] == 50.0
    assert len(respuesta["alertas"]) == 1

    assert servicio.ultima_consulta_historial["paciente_id"] == PACIENTE_ID
