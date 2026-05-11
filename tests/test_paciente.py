import os
import sys
from unittest.mock import MagicMock

from bson import ObjectId
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_paciente
from backend.main import app
from backend.routes import patient_route


client = TestClient(app)

USUARIO_ID = "69fe993245cf9ab8c39e4993"

PACIENTE_ID = ObjectId("69feaac76a52afc46ed40c52")

TOKEN_FALSO = HTTPAuthorizationCredentials(
    scheme="Bearer",
    credentials="token-test"
)

HEADER_TOKEN = "Bearer token-test"


def paciente_valido():
    return {
        "nombres": "Juan",
        "apellidos": "Perez",
        "fecha_nacimiento": "01/15/1990",
        "genero": "Masculino",
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension",
        "alergias_conocidas": "Ninguna",
        "observaciones_adicionales": "Paciente de prueba"
    }


# =========================
# VALIDACIONES
# =========================

def test_validar_paciente_exitoso():
    errores = validar_paciente(paciente_valido())
    assert errores == []


def test_nombre_vacio():
    data = paciente_valido()
    data["nombres"] = ""

    errores = validar_paciente(data)

    assert "El nombre es obligatorio" in errores


def test_apellidos_vacios():
    data = paciente_valido()
    data["apellidos"] = ""

    errores = validar_paciente(data)

    assert "Los apellidos son obligatorios" in errores


def test_fecha_invalida():
    data = paciente_valido()
    data["fecha_nacimiento"] = "1990-01-15"

    errores = validar_paciente(data)

    assert "La fecha de nacimiento debe tener formato mm/dd/yyyy" in errores


def test_fecha_futura():
    data = paciente_valido()
    data["fecha_nacimiento"] = "12/31/2099"

    errores = validar_paciente(data)

    assert "La fecha de nacimiento no puede ser futura" in errores


def test_genero_invalido():
    data = paciente_valido()
    data["genero"] = "Alien"

    errores = validar_paciente(data)

    assert any("El género debe ser uno de" in e for e in errores)


def test_tipo_documento_invalido():
    data = paciente_valido()
    data["tipo_documento"] = "XYZ"

    errores = validar_paciente(data)

    assert any("El tipo de documento debe ser uno de" in e for e in errores)


def test_documento_invalido():
    data = paciente_valido()
    data["numero_documento"] = "ABC123"

    errores = validar_paciente(data)

    assert "El número de documento debe contener solo números" in errores


def test_telefono_invalido():
    data = paciente_valido()
    data["telefono_contacto"] = "123"

    errores = validar_paciente(data)

    assert "El teléfono debe contener solo números y tener entre 7 y 10 dígitos" in errores


def test_faltan_campos_obligatorios():
    data = paciente_valido()
    del data["eps_aseguradora"]

    errores = validar_paciente(data)

    assert "La EPS/aseguradora es obligatoria" in errores


# =========================
# JWT
# =========================

def test_obtener_cuidador_id_ok(monkeypatch):
    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    cuidador_id = patient_route.obtener_cuidador_id(TOKEN_FALSO)

    assert cuidador_id == USUARIO_ID


def test_obtener_cuidador_id_sin_token():
    try:
        patient_route.obtener_cuidador_id(None)
        assert False

    except Exception as e:
        assert e.status_code == 401
        assert e.detail == "Token no proporcionado"


def test_obtener_cuidador_id_token_invalido(monkeypatch):
    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: None
    )

    try:
        patient_route.obtener_cuidador_id(TOKEN_FALSO)
        assert False

    except Exception as e:
        assert e.status_code == 401
        assert e.detail == "Token inválido o expirado"


# =========================
# POST /pacientes
# =========================

def test_post_paciente_exitoso(monkeypatch):
    data = paciente_valido()

    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = None

    insert_result = MagicMock()
    insert_result.inserted_id = PACIENTE_ID

    pacientes_col_falsa.insert_one.return_value = insert_result

    monkeypatch.setattr(
        patient_route,
        "pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.post(
        "/pacientes",
        json=data,
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 201

    cuerpo = response.json()

    assert cuerpo["message"] == "Paciente registrado exitosamente"
    assert cuerpo["paciente_id"] == str(PACIENTE_ID)

    documento = pacientes_col_falsa.insert_one.call_args.args[0]

    assert documento["nombres"] == "Juan"
    assert documento["apellidos"] == "Perez"
    assert documento["cuidador_id"] == USUARIO_ID


def test_post_paciente_datos_invalidos(monkeypatch):
    data = paciente_valido()
    data["nombres"] = ""

    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.post(
        "/pacientes",
        json=data,
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 400
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_post_paciente_duplicado(monkeypatch):
    data = paciente_valido()

    pacientes_col_falsa = MagicMock()

    pacientes_col_falsa.find_one.return_value = {
        "_id": PACIENTE_ID,
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "cuidador_id": USUARIO_ID
    }

    monkeypatch.setattr(
        patient_route,
        "pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.post(
        "/pacientes",
        json=data,
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un paciente con ese documento"


def test_post_paciente_sin_token():
    response = client.post(
        "/pacientes",
        json=paciente_valido()
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# =========================
# GET /pacientes
# =========================

def test_get_pacientes_exitoso(monkeypatch):
    pacientes_col_falsa = MagicMock()

    pacientes_col_falsa.find.return_value = [
        {
            "_id": PACIENTE_ID,
            "nombres": "Juan",
            "apellidos": "Perez",
            "fecha_nacimiento": "01/15/1990",
            "genero": "Masculino",
            "tipo_documento": "CC",
            "numero_documento": "12345678",
            "telefono_contacto": "3001234567",
            "eps_aseguradora": "Sura",
            "diagnostico_principal": "Hipertension",
            "alergias_conocidas": "Ninguna",
            "observaciones_adicionales": "Paciente de prueba",
            "cuidador_id": USUARIO_ID
        }
    ]

    tomas_col_falsa = MagicMock()
    tomas_col_falsa.count_documents.return_value = 0

    monkeypatch.setattr(
        patient_route,
        "pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        patient_route,
        "tomas_col",
        tomas_col_falsa
    )

    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.get(
        "/pacientes",
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 200

    cuerpo = response.json()

    assert len(cuerpo) == 1
    assert cuerpo[0]["id"] == str(PACIENTE_ID)
    assert cuerpo[0]["nombres"] == "Juan"
    assert cuerpo[0]["alerta"]["tiene_alerta"] is False


def test_get_paciente_por_id_exitoso(monkeypatch):
    pacientes_col_falsa = MagicMock()

    pacientes_col_falsa.find_one.return_value = {
        "_id": PACIENTE_ID,
        "nombres": "Juan",
        "apellidos": "Perez",
        "fecha_nacimiento": "01/15/1990",
        "genero": "Masculino",
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension",
        "alergias_conocidas": "Ninguna",
        "observaciones_adicionales": "Paciente de prueba",
        "cuidador_id": USUARIO_ID
    }

    monkeypatch.setattr(
        patient_route,
        "pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.get(
        f"/pacientes/{str(PACIENTE_ID)}",
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 200

    cuerpo = response.json()

    assert cuerpo["id"] == str(PACIENTE_ID)
    assert cuerpo["nombres"] == "Juan"


def test_get_paciente_por_id_no_encontrado(monkeypatch):
    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = None

    monkeypatch.setattr(
        patient_route,
        "pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.get(
        f"/pacientes/{str(PACIENTE_ID)}",
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Paciente no encontrado"


def test_get_paciente_por_id_invalido(monkeypatch):
    monkeypatch.setattr(
        patient_route,
        "verify_jwt",
        lambda token: {"id": USUARIO_ID}
    )

    response = client.get(
        "/pacientes/id-invalido",
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "ID de paciente inválido"