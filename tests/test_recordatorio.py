import pytest
from unittest.mock import MagicMock
from bson import ObjectId
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.validaciones import validar_recordatorio
from backend.main import app
from backend.routes import reminder_route


client = TestClient(app)

MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
PACIENTE_ID = "69feaac76a52afc46ed40c52"
RECORDATORIO_ID = ObjectId("507f1f77bcf86cd799439011")


def recordatorio_valido():
    return {
        "medicamento_id": MEDICAMENTO_ID,
        "hora_recordatorio": "08:30",
        "fecha_inicio": "03/25/2026",
        "activo": 1,
        "observaciones": "Prueba",
    }


# =========================
# VALIDACIONES
# =========================

def test_validar_recordatorio_exitoso():
    errores = validar_recordatorio(recordatorio_valido())
    assert errores == []


def test_medicamento_id_faltante():
    data = recordatorio_valido()
    del data["medicamento_id"]

    errores = validar_recordatorio(data)

    assert "La id del medicamento es obligatoria" in errores


def test_hora_recordatorio_vacia():
    data = recordatorio_valido()
    data["hora_recordatorio"] = ""

    errores = validar_recordatorio(data)

    assert "Favor ingresar la hora del recordatorio" in errores


def test_fecha_inicio_vacia():
    data = recordatorio_valido()
    data["fecha_inicio"] = ""

    errores = validar_recordatorio(data)

    assert "Se requiere la fecha de inicio" in errores


def test_medicamento_id_invalido_texto():
    data = recordatorio_valido()
    data["medicamento_id"] = "abc"

    errores = validar_recordatorio(data)

    assert "El medicamento_id debe ser un ObjectId válido" in errores


def test_medicamento_id_invalido_numero():
    data = recordatorio_valido()
    data["medicamento_id"] = 0

    errores = validar_recordatorio(data)

    assert "El medicamento_id debe ser un ObjectId válido" in errores


def test_hora_formato_invalido():
    data = recordatorio_valido()
    data["hora_recordatorio"] = "8pm"

    errores = validar_recordatorio(data)

    assert "La hora del recordatorio debe tener formato HH:MM" in errores


def test_fecha_inicio_formato_invalido():
    data = recordatorio_valido()
    data["fecha_inicio"] = "2026-03-25"

    errores = validar_recordatorio(data)

    assert "La fecha de inicio debe tener formato mm/dd/yyyy" in errores


def test_activo_invalido():
    data = recordatorio_valido()
    data["activo"] = 5

    errores = validar_recordatorio(data)

    assert "El campo activo debe ser 0 o 1" in errores


def test_hora_limite_inferior():
    data = recordatorio_valido()
    data["hora_recordatorio"] = "00:00"

    errores = validar_recordatorio(data)

    assert errores == []


def test_hora_limite_superior():
    data = recordatorio_valido()
    data["hora_recordatorio"] = "23:59"

    errores = validar_recordatorio(data)

    assert errores == []


def test_recordatorio_inactivo():
    data = recordatorio_valido()
    data["activo"] = 0

    errores = validar_recordatorio(data)

    assert errores == []


# =========================
# ENDPOINT POST / FUNCIÓN
# =========================

def test_post_recordatorio_exitoso(monkeypatch):
    data = recordatorio_valido()

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "paciente_id": PACIENTE_ID,
        "nombre": "Aspirina",
        "dosis": "1 tableta"
    }

    recordatorios_col_falsa = MagicMock()
    insert_result = MagicMock()
    insert_result.inserted_id = RECORDATORIO_ID
    recordatorios_col_falsa.insert_one.return_value = insert_result

    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos_col_falsa)
    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios_col_falsa)
    monkeypatch.setattr(reminder_route, "publisher", None)

    respuesta = reminder_route.crear_recordatorio(data)

    assert respuesta["mensaje"] == "Recordatorio creado correctamente"
    assert respuesta["recordatorio_id"] == str(RECORDATORIO_ID)

    recordatorios_col_falsa.insert_one.assert_called_once()
    documento = recordatorios_col_falsa.insert_one.call_args.args[0]

    assert documento["medicamento_id"] == MEDICAMENTO_ID
    assert documento["paciente_id"] == PACIENTE_ID
    assert documento["hora_recordatorio"] == data["hora_recordatorio"].strip()
    assert documento["fecha_inicio"] == data["fecha_inicio"].strip()
    assert documento["activo"] == int(data.get("activo", 1))
    assert documento["observaciones"] == data.get("observaciones", "").strip()
    assert documento["tomado"] is False


def test_post_recordatorio_datos_invalidos(monkeypatch):
    data = recordatorio_valido()
    data["hora_recordatorio"] = ""

    response = client.post("/recordatorios/", json=data)

    assert response.status_code == 400
    assert "Favor ingresar la hora del recordatorio" in response.json()["detail"]


def test_post_recordatorio_medicamento_no_existe(monkeypatch):
    data = recordatorio_valido()

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = None

    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos_col_falsa)

    with pytest.raises(HTTPException) as exc_info:
        reminder_route.crear_recordatorio(data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "El medicamento no existe"


def test_post_recordatorio_medicamento_sin_paciente(monkeypatch):
    data = recordatorio_valido()

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "nombre": "Aspirina"
    }

    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos_col_falsa)

    with pytest.raises(HTTPException) as exc_info:
        reminder_route.crear_recordatorio(data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "El medicamento no tiene paciente asociado"


# =========================
# ENDPOINT GET / FUNCIÓN
# =========================

def test_get_recordatorios_lista_vacia(monkeypatch):
    recordatorios_col_falsa = MagicMock()
    recordatorios_col_falsa.find.return_value = []

    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios_col_falsa)

    respuesta = reminder_route.listar_recordatorios(PACIENTE_ID)

    assert respuesta == {"recordatorios": []}


def test_get_recordatorios_exitoso(monkeypatch):
    recordatorios_col_falsa = MagicMock()
    recordatorios_col_falsa.find.return_value = [
        {
            "_id": RECORDATORIO_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "paciente_id": PACIENTE_ID,
            "hora_recordatorio": "08:30",
            "fecha_inicio": "03/25/2026",
            "activo": 1,
            "observaciones": "Prueba",
            "tomado": False
        }
    ]

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "nombre": "Acetaminofen",
        "dosis": "500 mg",
        "paciente_id": PACIENTE_ID
    }

    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios_col_falsa)
    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos_col_falsa)

    respuesta = reminder_route.listar_recordatorios(PACIENTE_ID)

    assert "recordatorios" in respuesta
    assert len(respuesta["recordatorios"]) == 1

    r = respuesta["recordatorios"][0]

    assert r["id"] == str(RECORDATORIO_ID)
    assert r["medicamento_id"] == MEDICAMENTO_ID
    assert r["paciente_id"] == PACIENTE_ID
    assert r["medicamento_nombre"] == "Acetaminofen"
    assert r["dosis"] == "500 mg"
    assert r["hora_recordatorio"] == "08:30"
    assert r["fecha_inicio"] == "03/25/2026"
    assert r["activo"] == 1
    assert r["observaciones"] == "Prueba"
    assert r["tomado"] is False


def test_get_recordatorios_endpoint_exitoso(monkeypatch):
    recordatorios_col_falsa = MagicMock()
    recordatorios_col_falsa.find.return_value = [
        {
            "_id": RECORDATORIO_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "paciente_id": PACIENTE_ID,
            "hora_recordatorio": "08:30",
            "fecha_inicio": "03/25/2026",
            "activo": 1,
            "observaciones": "Prueba",
            "tomado": False
        }
    ]

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "nombre": "Acetaminofen",
        "dosis": "500 mg",
        "paciente_id": PACIENTE_ID
    }

    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios_col_falsa)
    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos_col_falsa)

    response = client.get(f"/recordatorios/{PACIENTE_ID}")

    assert response.status_code == 200

    cuerpo = response.json()

    assert "recordatorios" in cuerpo
    assert len(cuerpo["recordatorios"]) == 1
    assert cuerpo["recordatorios"][0]["medicamento_nombre"] == "Acetaminofen"
    assert cuerpo["recordatorios"][0]["hora_recordatorio"] == "08:30"