import os
import sys
from unittest.mock import MagicMock

from bson import ObjectId
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.factories.paciente_factory import PacienteGeneralFactory, PacienteGeneral
from backend.main import app
from backend.routes import patient_route


client = TestClient(app)

USUARIO_ID = "69fe993245cf9ab8c39e4993"
PACIENTE_ID = ObjectId("69feaac76a52afc46ed40c52")

TOKEN_OBJETO = HTTPAuthorizationCredentials(
    scheme="Bearer",
    credentials="token-test"
)

HEADER_TOKEN = "Bearer token-test"


def datos_validos():
    return {
        "nombres": "Laura",
        "apellidos": "Gomez",
        "fecha_nacimiento": "05/10/1990",
        "genero": "Femenino",
        "tipo_documento": "CC",
        "numero_documento": "1020304050",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension",
    }


# =========================
# PRUEBAS DE LA FÁBRICA
# =========================

def test_fabrica_devuelve_paciente_general():
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    assert isinstance(paciente, PacienteGeneral)


def test_fabrica_limpia_espacios_en_blanco():
    fabrica = PacienteGeneralFactory()

    data = datos_validos()
    data["nombres"] = "  Laura  "
    data["apellidos"] = "  Gomez  "

    paciente = fabrica.crear(data)

    assert paciente.nombres == "Laura"
    assert paciente.apellidos == "Gomez"


def test_fabrica_maneja_campos_opcionales_ausentes():
    fabrica = PacienteGeneralFactory()

    paciente = fabrica.crear(datos_validos())

    assert paciente.alergias_conocidas == ""
    assert paciente.observaciones_adicionales == ""


def test_to_tuple_tiene_11_elementos_en_orden_correcto():
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    tupla = paciente.como_tupla()

    assert len(tupla) == 11
    assert tupla[0] == "Laura"
    assert tupla[1] == "Gomez"
    assert tupla[4] == "CC"
    assert tupla[5] == "1020304050"


def test_como_dict_tiene_campos_correctos():
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    doc = paciente.como_dict()

    assert doc["nombres"] == "Laura"
    assert doc["apellidos"] == "Gomez"
    assert doc["tipo_documento"] == "CC"
    assert doc["numero_documento"] == "1020304050"
    assert doc["eps_aseguradora"] == "Sura"


# =========================
# PRUEBAS DEL ENDPOINT POST /pacientes
# =========================

def test_caso_valido_endpoint_responde_201(monkeypatch):
    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = None

    insert_result = MagicMock()
    insert_result.inserted_id = PACIENTE_ID
    pacientes_col_falsa.insert_one.return_value = insert_result

    monkeypatch.setattr(patient_route, "pacientes_col", pacientes_col_falsa)
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    response = client.post(
        "/pacientes",
        json=datos_validos(),
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 201

    body = response.json()

    assert body["message"] == "Paciente registrado exitosamente"
    assert body["paciente_id"] == str(PACIENTE_ID)

    pacientes_col_falsa.insert_one.assert_called_once()

    documento = pacientes_col_falsa.insert_one.call_args.args[0]

    assert documento["nombres"] == "Laura"
    assert documento["apellidos"] == "Gomez"
    assert documento["cuidador_id"] == USUARIO_ID


def test_campo_nombres_vacio_responde_400(monkeypatch):
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    data = datos_validos()
    data["nombres"] = ""

    response = client.post(
        "/pacientes",
        json=data,
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 400
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_falta_campo_obligatorio_responde_400(monkeypatch):
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    data = datos_validos()
    del data["eps_aseguradora"]

    response = client.post(
        "/pacientes",
        json=data,
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 400
    assert "La EPS/aseguradora es obligatoria" in response.json()["detail"]


def test_body_casi_vacio_responde_400_con_multiples_errores(monkeypatch):
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    response = client.post(
        "/pacientes",
        json={"nombres": "Laura"},
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 400

    errores = response.json()["detail"]
    assert len(errores) > 1


def test_caso_duplicado_responde_409(monkeypatch):
    pacientes_col_falsa = MagicMock()

    pacientes_col_falsa.find_one.return_value = {
        "_id": PACIENTE_ID,
        "tipo_documento": "CC",
        "numero_documento": "1020304050",
        "cuidador_id": USUARIO_ID
    }

    monkeypatch.setattr(patient_route, "pacientes_col", pacientes_col_falsa)
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    response = client.post(
        "/pacientes",
        json=datos_validos(),
        headers={"Authorization": HEADER_TOKEN}
    )

    assert response.status_code == 409
    assert "Ya existe un paciente con ese documento" in response.json()["detail"]


def test_endpoint_sin_token_responde_401():
    response = client.post(
        "/pacientes",
        json=datos_validos()
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
