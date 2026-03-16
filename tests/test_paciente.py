import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_paciente, verificar_duplicado
from backend.main import app

client = TestClient(app)


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
        "diagnostico_principal": "Hipertension"
    }


def test_validar_paciente_exitoso():
    data = paciente_valido()
    errores = validar_paciente(data)
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


def test_verificar_duplicado_devuelve_true_si_existe():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            genero TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            telefono_contacto TEXT NOT NULL,
            eps_aseguradora TEXT,
            diagnostico_principal TEXT,
            alergias_conocidas TEXT,
            observaciones_adicionales TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO pacientes (
            nombres, apellidos, fecha_nacimiento, genero,
            tipo_documento, numero_documento, telefono_contacto,
            eps_aseguradora, diagnostico_principal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Juan", "Perez", "01/15/1990", "Masculino",
        "CC", "12345678", "3001234567", "Sura", "Hipertension"
    ))

    conn.commit()

    resultado = verificar_duplicado("12345678", "CC", conn)

    assert resultado is True
    conn.close()


def test_verificar_duplicado_devuelve_false_si_no_existe():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            genero TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            telefono_contacto TEXT NOT NULL,
            eps_aseguradora TEXT,
            diagnostico_principal TEXT,
            alergias_conocidas TEXT,
            observaciones_adicionales TEXT
        )
    """)

    conn.commit()

    resultado = verificar_duplicado("99999999", "CC", conn)

    assert resultado is False
    conn.close()


def test_post_paciente_exitoso():
    data = paciente_valido()

    conexion_falsa = MagicMock()
    cursor_falso = MagicMock()
    cursor_falso.lastrowid = 1
    conexion_falsa.cursor.return_value = cursor_falso

    with patch("backend.routes.patient_route.get_connection", return_value=conexion_falsa), \
         patch("backend.routes.patient_route.verificar_duplicado", return_value=False):

        response = client.post("/pacientes", json=data)

    assert response.status_code == 201
    assert response.json()["message"] == "Paciente registrado exitosamente"
    assert response.json()["paciente_id"] == 1


def test_post_paciente_datos_invalidos():
    data = paciente_valido()
    data["nombres"] = ""

    response = client.post("/pacientes", json=data)

    assert response.status_code == 400
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_post_paciente_duplicado():
    data = paciente_valido()

    conexion_falsa = MagicMock()

    with patch("backend.routes.patient_route.get_connection", return_value=conexion_falsa), \
         patch("backend.routes.patient_route.verificar_duplicado", return_value=True):

        response = client.post("/pacientes", json=data)

    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un paciente con ese documento"