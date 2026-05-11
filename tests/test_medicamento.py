import os
import sys
from unittest.mock import MagicMock

from bson import ObjectId
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_medicamento
from backend.main import app
from backend.routes import medication_route


client = TestClient(app)

PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = ObjectId("69feb355322be070cd1c97ce")


def medicamento_valido():
    return {
        "nombre_medicamento": "Acetaminofen",
        "concentracion": "500 mg",
        "forma_farmaceutica": "Tableta",
        "dosis_cantidad": 1,
        "dosis_unidad": "tableta",
        "frecuencia": "Cada 8 horas",
        "fecha_inicio": "03/16/2026",
        "paciente_id": PACIENTE_ID,
        "horarios": ["08:00", "16:00", "00:00"],
        "observaciones": "Tomar después de comer"
    }


# =========================
# PRUEBAS DE VALIDACIONES
# =========================

def test_validar_medicamento_exitoso():
    errores = validar_medicamento(medicamento_valido())
    assert errores == []


def test_nombre_medicamento_vacio():
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    errores = validar_medicamento(data)

    assert "El nombre del medicamento es obligatorio" in errores


def test_dosis_vacia():
    data = medicamento_valido()
    data["dosis_cantidad"] = ""

    errores = validar_medicamento(data)

    assert "La dosis es obligatoria" in errores


def test_frecuencia_vacia():
    data = medicamento_valido()
    data["frecuencia"] = ""

    errores = validar_medicamento(data)

    assert "La frecuencia es obligatoria" in errores


def test_horario_vacio():
    data = medicamento_valido()
    data["horarios"] = []

    errores = validar_medicamento(data)

    assert "Debe ingresar al menos un horario" in errores


def test_fecha_inicio_vacia():
    data = medicamento_valido()
    data["fecha_inicio"] = ""

    errores = validar_medicamento(data)

    assert "La fecha de inicio es obligatoria" in errores


def test_paciente_id_faltante():
    data = medicamento_valido()
    del data["paciente_id"]

    errores = validar_medicamento(data)

    assert "El paciente_id es obligatorio" in errores


def test_paciente_id_invalido_texto():
    data = medicamento_valido()
    data["paciente_id"] = "abc"

    errores = validar_medicamento(data)

    assert "El paciente_id debe ser un ObjectId válido" in errores


def test_paciente_id_invalido_numero():
    data = medicamento_valido()
    data["paciente_id"] = 0

    errores = validar_medicamento(data)

    assert "El paciente_id debe ser un ObjectId válido" in errores


# =========================
# PRUEBAS DEL ENDPOINT POST
# =========================

def test_post_medicamento_exitoso(monkeypatch):
    data = medicamento_valido()

    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = {
        "_id": ObjectId(PACIENTE_ID),
        "nombres": "Juan",
        "apellidos": "Perez"
    }

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = None

    insert_result = MagicMock()
    insert_result.inserted_id = MEDICAMENTO_ID
    medicamentos_col_falsa.insert_one.return_value = insert_result

    monkeypatch.setattr(medication_route, "pacientes_col", pacientes_col_falsa)
    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos_col_falsa)

    response = client.post("/medicamentos/", json=data)

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Medicamento registrado exitosamente"

    medicamentos_col_falsa.insert_one.assert_called_once()

    documento = medicamentos_col_falsa.insert_one.call_args.args[0]

    assert documento["nombre"] == "acetaminofen"
    assert documento["dosis"] == "1 tableta"
    assert documento["frecuencia"] == "Cada 8 horas"
    assert documento["horario"] == "08:00, 16:00, 00:00"
    assert documento["fecha_inicio"] == "03/16/2026"
    assert documento["paciente_id"] == PACIENTE_ID
    assert "Concentración: 500 mg" in documento["observaciones"]
    assert "Forma farmacéutica: Tableta" in documento["observaciones"]


def test_post_medicamento_datos_invalidos():
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    response = client.post("/medicamentos/", json=data)

    assert response.status_code == 400
    assert "El nombre del medicamento es obligatorio" in response.json()["detail"]


def test_post_medicamento_paciente_id_invalido(monkeypatch):
    data = medicamento_valido()
    data["paciente_id"] = "id-invalido"

    response = client.post("/medicamentos/", json=data)

    assert response.status_code == 400
    assert "El paciente_id debe ser un ObjectId válido" in response.json()["detail"]


def test_post_medicamento_paciente_no_existe(monkeypatch):
    data = medicamento_valido()

    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = None

    monkeypatch.setattr(medication_route, "pacientes_col", pacientes_col_falsa)

    response = client.post("/medicamentos/", json=data)

    assert response.status_code == 404
    assert response.json()["detail"] == "El paciente no existe"


def test_post_medicamento_duplicado(monkeypatch):
    data = medicamento_valido()

    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = {
        "_id": ObjectId(PACIENTE_ID)
    }

    medicamentos_col_falsa = MagicMock()
    medicamentos_col_falsa.find_one.return_value = {
        "_id": MEDICAMENTO_ID,
        "paciente_id": PACIENTE_ID,
        "nombre": "acetaminofen"
    }

    monkeypatch.setattr(medication_route, "pacientes_col", pacientes_col_falsa)
    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos_col_falsa)

    response = client.post("/medicamentos/", json=data)

    assert response.status_code == 400
    assert response.json()["detail"] == "El paciente ya tiene registrado este medicamento"


# =========================
# PRUEBAS DEL ENDPOINT GET
# =========================

def test_get_medicamentos_paciente_exitoso(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [
        {
            "_id": MEDICAMENTO_ID,
            "nombre": "acetaminofen",
            "dosis": "1 tableta",
            "frecuencia": "Cada 8 horas",
            "horario": "08:00, 16:00, 00:00",
            "fecha_inicio": "03/16/2026",
            "observaciones": "Concentración: 500 mg | Forma farmacéutica: Tableta",
            "paciente_id": PACIENTE_ID
        }
    ]

    medicamentos_col_falsa.find.return_value = cursor_mock

    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos_col_falsa)

    response = client.get(f"/medicamentos/paciente/{PACIENTE_ID}")

    assert response.status_code == 200

    cuerpo = response.json()

    assert len(cuerpo) == 1
    assert cuerpo[0]["id"] == str(MEDICAMENTO_ID)
    assert cuerpo[0]["nombre"] == "acetaminofen"
    assert cuerpo[0]["paciente_id"] == PACIENTE_ID


def test_get_medicamentos_paciente_vacio(monkeypatch):
    medicamentos_col_falsa = MagicMock()

    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = []

    medicamentos_col_falsa.find.return_value = cursor_mock

    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos_col_falsa)

    response = client.get(f"/medicamentos/paciente/{PACIENTE_ID}")

    assert response.status_code == 200
    assert response.json() == []