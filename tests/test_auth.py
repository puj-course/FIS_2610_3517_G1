import sys
sys.path.insert(0, "./backend")

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import get_connection
from backend.auth import hash_password


@pytest.fixture
def cliente():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM usuarios WHERE correo = ?",
        ("admin@medtrack.com",)
    )

    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, contrasena, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Admin Test",
        "admin@medtrack.com",
        hash_password("admin123"),
        "administrador"
    ))

    conn.commit()
    conn.close()

    return TestClient(app)


def test_login_exitoso(cliente):
    respuesta = cliente.post("/signin", json={
        "username": "admin@medtrack.com",
        "password": "admin123"
    })
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert "token" in datos


def test_login_contrasena_incorrecta(cliente):
    respuesta = cliente.post("/signin", json={
        "username": "admin@medtrack.com",
        "password": "wrongpassword"
    })
    assert respuesta.status_code == 401


def test_login_usuario_no_existe(cliente):
    respuesta = cliente.post("/signin", json={
        "username": "noexiste@medtrack.com",
        "password": "admin123"
    })
    assert respuesta.status_code == 401


def test_login_campos_vacios(cliente):
    respuesta = cliente.post("/signin", json={})
    assert respuesta.status_code == 422  # FastAPI valida esquema


def test_login_sin_contrasena(cliente):
    respuesta = cliente.post("/signin", json={
        "username": "admin@medtrack.com"
    })
    assert respuesta.status_code == 422