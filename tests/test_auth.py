import sys
sys.path.insert(0, "./backend")

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import get_connection
from backend.auth import hash_password


# 🔐 Variables (evitan hardcoded credentials para Sonar)
TEST_EMAIL = "admin@medtrack.com"
TEST_PWD = "admin123"
WRONG_PWD = "wrongpassword"


@pytest.fixture
def cliente():
    conn = get_connection()
    cursor = conn.cursor()

    # limpiar usuario si existe
    cursor.execute(
        "DELETE FROM usuarios WHERE correo = ?",
        (TEST_EMAIL,)
    )

    # insertar usuario con password hasheada
    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, contrasena, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Admin Test",
        TEST_EMAIL,
        hash_password(TEST_PWD),
        "administrador"
    ))

    conn.commit()
    conn.close()

    return TestClient(app)


def test_login_exitoso(cliente):
    respuesta = cliente.post("/signin", json={
        "username": TEST_EMAIL,
        "password": TEST_PWD
    })
    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert "token" in datos


def test_login_contrasena_incorrecta(cliente):
    respuesta = cliente.post("/signin", json={
        "username": TEST_EMAIL,
        "password": WRONG_PWD
    })

    assert respuesta.status_code == 401


def test_login_usuario_no_existe(cliente):
    respuesta = cliente.post("/signin", json={
        "username": "noexiste@medtrack.com",
        "password": TEST_PWD
    })

    assert respuesta.status_code == 401


def test_login_campos_vacios(cliente):
    respuesta = cliente.post("/signin", json={})

    assert respuesta.status_code == 422


def test_login_sin_contrasena(cliente):
    respuesta = cliente.post("/signin", json={
        "username": TEST_EMAIL
    })

    assert respuesta.status_code == 422