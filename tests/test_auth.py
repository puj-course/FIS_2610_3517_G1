import os
import sys

from bson import ObjectId
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.auth import hash_password
from backend.routes import auth_route


client = TestClient(app)

TEST_EMAIL = "admin@medtrack.com"
TEST_KEY = "admin123"
WRONG_KEY = "wrong123"

USUARIO_ID = ObjectId("69ff0c5cb77969e0f2d52a11")


class ColeccionUsuariosFalsa:
    """
    Colección falsa para simular usuarios_col de MongoDB.

    Permite probar /signin sin conectarse a MongoDB Atlas.
    """

    def __init__(self, usuario=None):
        self.usuario = usuario

    def find_one(self, filtro):
        correo = filtro.get("correo")

        if self.usuario and correo == self.usuario["correo"]:
            return self.usuario

        return None


def usuario_mock():
    """
    Usuario válido de prueba.

    La contraseña se guarda hasheada porque auth_route compara contra hash.
    """
    return {
        "_id": USUARIO_ID,
        "nombre": "Admin Test",
        "correo": TEST_EMAIL,
        "contrasena": hash_password(TEST_KEY),
        "rol": "administrador"
    }


# =========================
# LOGIN EXITOSO
# =========================

def test_login_exitoso(monkeypatch):
    usuarios_col_falsa = ColeccionUsuariosFalsa(usuario_mock())

    monkeypatch.setattr(
        auth_route,
        "usuarios_col",
        usuarios_col_falsa
    )

    respuesta = client.post("/signin", json={
        "username": TEST_EMAIL,
        "password": TEST_KEY
    })

    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert "token" in datos
    assert datos["usuario"]["correo"] == TEST_EMAIL
    assert datos["usuario"]["rol"] == "administrador"


# =========================
# CONTRASEÑA INCORRECTA
# =========================

def test_login_contrasena_incorrecta(monkeypatch):
    usuarios_col_falsa = ColeccionUsuariosFalsa(usuario_mock())

    monkeypatch.setattr(
        auth_route,
        "usuarios_col",
        usuarios_col_falsa
    )

    respuesta = client.post("/signin", json={
        "username": TEST_EMAIL,
        "password": WRONG_KEY
    })

    assert respuesta.status_code == 401
    assert "Usuario o contraseña incorrectos" in respuesta.json()["detail"]


# =========================
# USUARIO NO EXISTE
# =========================

def test_login_usuario_no_existe(monkeypatch):
    usuarios_col_falsa = ColeccionUsuariosFalsa(None)

    monkeypatch.setattr(
        auth_route,
        "usuarios_col",
        usuarios_col_falsa
    )

    respuesta = client.post("/signin", json={
        "username": "noexiste@medtrack.com",
        "password": TEST_KEY
    })

    assert respuesta.status_code == 401
    assert "Usuario o contraseña incorrectos" in respuesta.json()["detail"]


# =========================
# CAMPOS VACÍOS
# =========================

def test_login_campos_vacios():
    respuesta = client.post("/signin", json={})

    assert respuesta.status_code == 422


def test_login_sin_contrasena():
    respuesta = client.post("/signin", json={
        "username": TEST_EMAIL
    })

    assert respuesta.status_code == 422


def test_login_sin_username():
    respuesta = client.post("/signin", json={
        "password": TEST_KEY
    })

    assert respuesta.status_code == 422
