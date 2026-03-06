import sys
sys.path.insert(0, "./backend")

import pytest
from app import app

@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        yield cliente

def test_login_exitoso(cliente):
    respuesta = cliente.post("/login", json={
        "correo": "admin@medtrack.com",
        "contrasena": "admin123"
    })
    datos = respuesta.get_json()
    assert respuesta.status_code == 200
    assert "token" in datos

def test_login_contrasena_incorrecta(cliente):
    respuesta = cliente.post("/login", json={
        "correo": "admin@medtrack.com",
        "contrasena": "wrongpassword"
    })
    assert respuesta.status_code == 401

def test_login_usuario_no_existe(cliente):
    respuesta = cliente.post("/login", json={
        "correo": "noexiste@medtrack.com",
        "contrasena": "admin123"
    })
    assert respuesta.status_code == 401

def test_login_campos_vacios(cliente):
    respuesta = cliente.post("/login", json={})
    assert respuesta.status_code == 400

def test_login_sin_contrasena(cliente):
    respuesta = cliente.post("/login", json={
        "correo": "admin@medtrack.com"
    })
    assert respuesta.status_code == 400