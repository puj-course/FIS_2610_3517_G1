# test_medicamento.py
import os
import sys
from unittest.mock import MagicMock

from bson import ObjectId
from fastapi.testclient import TestClient

# Variables mínimas para que backend.database y el middleware puedan cargar
# correctamente durante pruebas locales y CI.
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/medtrack_test")
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-medtrack"

# Agregamos la raíz del proyecto al path para que pytest pueda importar backend
# correctamente cuando se ejecuta desde Git Bash.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_medicamento
from backend.main import app
from backend.auth import generate_jwt
from backend.routes import medication_route
import backend.auth as auth_module


# Aseguramos que los tokens se firmen con la misma clave que usa el middleware.
auth_module.SECRET_KEY = os.environ["SECRET_KEY"]

# TestClient = cliente HTTP falso que permite probar endpoints de FastAPI
# sin levantar el servidor con uvicorn.
client = TestClient(app)


PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = ObjectId("69feb355322be070cd1c97ce")


def headers_auth():
    """
    Construye el header Authorization para las pruebas del endpoint.

    Aunque algunos entornos de prueba usan TESTING=1, dejamos un token válido
    para que estos tests también funcionen localmente sin depender de esa variable.
    """
    token = generate_jwt(
        "cuidador-test-id",
        "admin@medtrack.com",
        "administrador"
    )

    return {
        "Authorization": f"Bearer {token}"
    }


def medicamento_valido():
    """
    Datos base válidos para registrar un medicamento.

    Importante:
    paciente_id debe ser un ObjectId válido porque medication_route.py
    consulta pacientes_col usando ObjectId(paciente_id).
    """
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
    """
    CASO VÁLIDO: todos los campos cumplen las reglas.

    validar_medicamento debe devolver una lista vacía.
    """
    errores = validar_medicamento(medicamento_valido())

    assert errores == []


def test_nombre_medicamento_vacio():
    """
    CASO INVÁLIDO: nombre_medicamento vacío.
    """
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    errores = validar_medicamento(data)

    assert "El nombre del medicamento es obligatorio" in errores


def test_dosis_vacia():
    """
    CASO INVÁLIDO: dosis_cantidad vacía.
    """
    data = medicamento_valido()
    data["dosis_cantidad"] = ""

    errores = validar_medicamento(data)

    assert "La dosis es obligatoria" in errores


def test_frecuencia_vacia():
    """
    CASO INVÁLIDO: frecuencia vacía.
    """
    data = medicamento_valido()
    data["frecuencia"] = ""

    errores = validar_medicamento(data)

    assert "La frecuencia es obligatoria" in errores


def test_horario_vacio():
    """
    CASO INVÁLIDO: lista de horarios vacía.
    """
    data = medicamento_valido()
    data["horarios"] = []

    errores = validar_medicamento(data)

    assert "Debe ingresar al menos un horario" in errores


def test_fecha_inicio_vacia():
    """
    CASO INVÁLIDO: fecha_inicio vacía.
    """
    data = medicamento_valido()
    data["fecha_inicio"] = ""

    errores = validar_medicamento(data)

    assert "La fecha de inicio es obligatoria" in errores


def test_paciente_id_faltante():
    """
    CASO INVÁLIDO: falta paciente_id.
    """
    data = medicamento_valido()
    del data["paciente_id"]

    errores = validar_medicamento(data)

    assert "El paciente_id es obligatorio" in errores


def test_paciente_id_invalido_texto():
    """
    CASO INVÁLIDO: paciente_id no es ObjectId.
    """
    data = medicamento_valido()
    data["paciente_id"] = "abc"

    errores = validar_medicamento(data)

    assert "El paciente_id debe ser un ObjectId válido" in errores


def test_paciente_id_invalido_numero():
    """
    CASO INVÁLIDO: paciente_id numérico viejo.

    Después de la migración a MongoDB, los IDs enteros ya no son válidos.
    """
    data = medicamento_valido()
    data["paciente_id"] = 0

    errores = validar_medicamento(data)

    assert "El paciente_id debe ser un ObjectId válido" in errores


# =========================
# PRUEBAS DEL ENDPOINT POST
# =========================

def test_post_medicamento_exitoso(monkeypatch):
    """
    CASO VÁLIDO DEL ENDPOINT POST /medicamentos/.

    La ruta actual usa MongoDB:
    1. Valida el body.
    2. Busca el paciente en pacientes_col usando ObjectId.
    3. Verifica duplicado en medicamentos_col.
    4. Inserta el medicamento en medicamentos_col.
    """
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

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Medicamento registrado exitosamente"
    assert response.json()["medicamento_id"] == str(MEDICAMENTO_ID)

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
    """
    CASO INVÁLIDO DEL ENDPOINT POST /medicamentos/.

    La validación debe fallar porque nombre_medicamento está vacío.
    """
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "El nombre del medicamento es obligatorio" in response.json()["detail"]


def test_post_medicamento_paciente_id_invalido():
    """
    CASO INVÁLIDO: paciente_id no tiene formato ObjectId.
    """
    data = medicamento_valido()
    data["paciente_id"] = "id-invalido"

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "El paciente_id debe ser un ObjectId válido" in response.json()["detail"]


def test_post_medicamento_paciente_no_existe(monkeypatch):
    """
    CASO INVÁLIDO: el paciente asociado no existe.
    """
    data = medicamento_valido()

    pacientes_col_falsa = MagicMock()
    pacientes_col_falsa.find_one.return_value = None

    monkeypatch.setattr(medication_route, "pacientes_col", pacientes_col_falsa)

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El paciente no existe"


def test_post_medicamento_duplicado(monkeypatch):
    """
    CASO INVÁLIDO: el paciente ya tiene registrado este medicamento.
    """
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

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "El paciente ya tiene registrado este medicamento"


# =========================
# PRUEBAS DEL ENDPOINT GET
# =========================

def test_get_medicamentos_paciente_exitoso(monkeypatch):
    """
    CASO VÁLIDO: consultar medicamentos de un paciente.
    """
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

    response = client.get(
        f"/medicamentos/paciente/{PACIENTE_ID}",
        headers=headers_auth()
    )

    assert response.status_code == 200

    cuerpo = response.json()

    assert len(cuerpo) == 1
    assert cuerpo[0]["id"] == str(MEDICAMENTO_ID)
    assert cuerpo[0]["nombre"] == "acetaminofen"
    assert cuerpo[0]["paciente_id"] == PACIENTE_ID


def test_get_medicamentos_paciente_vacio(monkeypatch):
    """
    CASO SIN MEDICAMENTOS: la consulta retorna lista vacía.
    """
    medicamentos_col_falsa = MagicMock()

    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = []

    medicamentos_col_falsa.find.return_value = cursor_mock

    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos_col_falsa)

    response = client.get(
        f"/medicamentos/paciente/{PACIENTE_ID}",
        headers=headers_auth()
    )

    assert response.status_code == 200
    assert response.json() == []