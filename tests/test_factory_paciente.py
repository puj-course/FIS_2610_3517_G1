import os
import sys
from unittest.mock import MagicMock

from bson import ObjectId
from fastapi.testclient import TestClient

# Clave fija para tests.
# El middleware usa os.getenv("SECRET_KEY") para validar el token.
# generate_jwt usa backend.auth.SECRET_KEY.
# Ambas deben coincidir para que TestClient pase por autenticación cuando
# TESTING no está activo.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-medtrack"

# Agregamos la raíz del proyecto al path para que pytest pueda importar backend
# correctamente cuando se ejecuta desde Git Bash.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.factories.paciente_factory import PacienteGeneralFactory, PacienteGeneral
from backend.main import app
from backend.auth import generate_jwt
from backend.routes import patient_route
import backend.auth as auth_module


# Aseguramos que los tokens se firmen con la misma clave que usa el middleware.
auth_module.SECRET_KEY = os.environ["SECRET_KEY"]

# TestClient = cliente HTTP falso que llama al endpoint sin levantar un servidor real.
# Es parecido a usar Postman, pero desde código.
client = TestClient(app)

USUARIO_ID = "69fe993245cf9ab8c39e4993"
PACIENTE_ID = ObjectId("69feaac76a52afc46ed40c52")


def headers_auth():
    """
    Construye el header Authorization para las pruebas del endpoint.

    La ruta POST /pacientes está protegida. Por eso enviamos un Bearer token
    válido para que la petición pueda pasar por el middleware global.
    """
    token = generate_jwt(
        USUARIO_ID,
        "admin@medtrack.com",
        "administrador"
    )

    return {
        "Authorization": f"Bearer {token}"
    }


def datos_validos():
    """
    Datos válidos base para construir y registrar un paciente.

    Se usan en pruebas de fábrica y en pruebas del endpoint.
    """
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
    """
    PRUEBA BÁSICA: la fábrica debe devolver un objeto PacienteGeneral.

    Paso a paso:
    1. Creamos la fábrica.
    2. Le pedimos que construya un paciente con datos válidos.
    3. Verificamos que el resultado sea una instancia de PacienteGeneral.
    """
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    assert isinstance(paciente, PacienteGeneral)


def test_fabrica_limpia_espacios_en_blanco():
    """
    La fábrica debe quitar espacios al inicio y al final de los campos.

    Esto es normalización:
    "  Laura  " debe quedar "Laura".
    """
    fabrica = PacienteGeneralFactory()

    data = datos_validos()
    data["nombres"] = "  Laura  "
    data["apellidos"] = "  Gomez  "

    paciente = fabrica.crear(data)

    assert paciente.nombres == "Laura"
    assert paciente.apellidos == "Gomez"


def test_fabrica_maneja_campos_opcionales_ausentes():
    """
    alergias_conocidas y observaciones_adicionales son opcionales.

    Si no vienen en el diccionario, la fábrica debe poner una cadena vacía
    en vez de lanzar un KeyError.
    """
    fabrica = PacienteGeneralFactory()

    paciente = fabrica.crear(datos_validos())

    assert paciente.alergias_conocidas == ""
    assert paciente.observaciones_adicionales == ""


def test_to_tuple_tiene_11_elementos_en_orden_correcto():
    """
    El método como_tupla() debe devolver exactamente 11 valores.

    Aunque la ruta actual de pacientes usa MongoDB, este método sigue siendo
    parte de la fábrica y puede ser usado por compatibilidad o por pruebas
    antiguas.
    """
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    tupla = paciente.como_tupla()

    assert len(tupla) == 11
    assert tupla[0] == "Laura"
    assert tupla[1] == "Gomez"
    assert tupla[4] == "CC"
    assert tupla[5] == "1020304050"


def test_como_dict_tiene_campos_correctos():
    """
    El método como_dict() debe construir el documento esperado para MongoDB.
    """
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
    """
    CASO VÁLIDO: enviar todos los campos correctos.

    Se simula pacientes_col con MagicMock para no conectarse a MongoDB real.
    También se parchea verify_jwt para controlar el cuidador_id.
    """
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
        headers=headers_auth()
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
    """
    CASO INVÁLIDO: nombres vacío.

    Como la ruta está protegida, se envía un token válido y se parchea
    verify_jwt para llegar a la validación del body.
    """
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    data = datos_validos()
    data["nombres"] = ""

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_falta_campo_obligatorio_responde_400(monkeypatch):
    """
    CASO INVÁLIDO: falta un campo obligatorio.
    """
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    data = datos_validos()
    del data["eps_aseguradora"]

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "La EPS/aseguradora es obligatoria" in response.json()["detail"]


def test_body_casi_vacio_responde_400_con_multiples_errores(monkeypatch):
    """
    CASO INVÁLIDO EXTREMO: body con un solo campo.

    Si alguien manda solo {"nombres": "Laura"} sin el resto de campos,
    deben aparecer múltiples errores de validación.
    """
    monkeypatch.setattr(patient_route, "verify_jwt", lambda token: {"id": USUARIO_ID})

    response = client.post(
        "/pacientes",
        json={"nombres": "Laura"},
        headers=headers_auth()
    )

    assert response.status_code == 400

    errores = response.json()["detail"]
    assert len(errores) > 1


def test_caso_duplicado_responde_409(monkeypatch):
    """
    CASO DUPLICADO: el paciente ya existe.

    Simulamos que pacientes_col.find_one() encuentra un paciente con el mismo:
    - tipo_documento
    - numero_documento
    - cuidador_id
    """
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
        headers=headers_auth()
    )

    assert response.status_code == 409
    assert "Ya existe un paciente con ese documento" in response.json()["detail"]


def test_endpoint_sin_token_responde_error_autenticacion():
    """
    CASO INVÁLIDO: no se envía token.

    Dependiendo de si responde el middleware global o HTTPBearer, FastAPI puede
    responder 401 o 403. En ambos casos representa rechazo por autenticación.
    """
    response = client.post(
        "/pacientes",
        json=datos_validos()
    )

    assert response.status_code in (401, 403)
    assert "detail" in response.json()
