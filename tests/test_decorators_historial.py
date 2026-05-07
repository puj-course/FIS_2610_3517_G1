#########################################################################################
#	test_decorators_historial.py
#######################################################################################
from backend.decorators.historial import (
    AlertasDecorator,
    CumplimientoDecorator,
    HistorialTomas,
)


# =========================
# HISTORIAL BASE
# =========================

def test_historial_tomas_devuelve_lista_base():
    tomas = [{"id": 1, "estado": "tomado"}]

    historial = HistorialTomas(tomas)

    assert historial.obtener_datos() == {"historial": tomas}


# =========================
# CUMPLIMIENTO
# =========================

def test_cumplimiento_decorator_calcula_porcentaje():
    tomas = [
        {"id": 1, "estado": "tomado"},
        {"id": 2, "estado": "a_tiempo"},
        {"id": 3, "estado": "tarde"},
        {"id": 4, "estado": "omitida"},
    ]

    historial = CumplimientoDecorator(HistorialTomas(tomas))
    datos = historial.obtener_datos()

    assert datos["cumplimiento"] == {
        "total_tomas": 4,
        "tomas_realizadas": 3,
        "porcentaje": 75.0,
    }


def test_cumplimiento_decorator_con_historial_vacio():
    historial = CumplimientoDecorator(HistorialTomas([]))
    datos = historial.obtener_datos()

    assert datos["cumplimiento"]["total_tomas"] == 0
    assert datos["cumplimiento"]["tomas_realizadas"] == 0
    assert datos["cumplimiento"]["porcentaje"] == 0


# =========================
# ALERTAS
# =========================

def test_alertas_decorator_agrega_alertas_para_tomas_pendientes():
    tomas = [
        {
            "medicamento_nombre": "Aspirina",
            "fecha": "2026-04-12",
            "hora_programada": "08:00",
            "estado": "pendiente",
        },
        {
            "medicamento_nombre": "Ibuprofeno",
            "fecha": "2026-04-12",
            "hora_programada": "14:00",
            "estado": "tomado",
        },
    ]

    historial = AlertasDecorator(HistorialTomas(tomas))
    datos = historial.obtener_datos()

    assert len(datos["alertas"]) == 1
    assert datos["alertas"][0]["medicamento"] == "Aspirina"
    assert "no registrada" in datos["alertas"][0]["mensaje"]
