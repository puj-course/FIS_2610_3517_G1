import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.auth import hash_password


TEST_EMAIL = "admin@medtrack.com"
TEST_KEY = "admin123"
WRONG_KEY = "wrong123"


class UsuariosColFalsa:
    def __init__(self, usuario=None):
        self.usuario = usuario

    def find_one(self, filtro):
        if not self.usuario:
            return None

        correo_buscado = filtro.get("correo")

        if correo_buscado == self.usuario.get("correo"):
            return self.usuario

        return None


@pytest.fixture
def cliente(monkeypatch):
    usuario = {
        "_id": "usuario-test-id",
        "nombre": "Admin Test",
        "correo": TEST_EMAIL,
        "contrasena": hash_password(TEST_KEY),
        "rol": "administrador",
    }

    monkeypatch.setattr(
        "backend.routes.auth_route.usuarios_col",
        UsuariosColFalsa(usuario)
    )

    return TestClient(app)


def test_login_exitoso(cliente):
    respuesta = cliente.post("/signin", json={
        "username": TEST_EMAIL,
        "password": TEST_KEY
    })

    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert "token" in datos
    assert datos["detail"] == "Inicio de sesión exitoso"
    assert datos["usuario"]["correo"] == TEST_EMAIL
    assert datos["usuario"]["rol"] == "administrador"


def test_login_contrasena_incorrecta(cliente):
    respuesta = cliente.post("/signin", json={
        "username": TEST_EMAIL,
        "password": WRONG_KEY
    })

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Usuario o contraseña incorrectos"


def test_login_usuario_no_existe(cliente):
    respuesta = cliente.post("/signin", json={
        "username": "noexiste@medtrack.com",
        "password": TEST_KEY
    })

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Usuario o contraseña incorrectos"


def test_login_campos_vacios(cliente):
    respuesta = cliente.post("/signin", json={})

    assert respuesta.status_code == 422


def test_login_sin_contrasena(cliente):
    respuesta = cliente.post("/signin", json={
        "username": TEST_EMAIL
    })

    assert respuesta.status_code == 422
