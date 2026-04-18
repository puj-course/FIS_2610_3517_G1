import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import (
    validar_medicamento,
    verificar_paciente_existe,
    verificar_medicamento_duplicado
)
from backend.main import app

client = TestClient(app)


def medicamento_valido():
    return {
        "nombre_medicamento": "Acetaminofen",
        "concentracion": "500 mg",
        "forma_farmaceutica": "Tableta",
        "dosis_cantidad": 1,
        "dosis_unidad": "tableta",
        "frecuencia": "Cada 8 horas",
        "fecha_inicio": "03/16/2026",
        "paciente_id": 1,
        "horarios": ["08:00", "16:00", "00:00"],
        "observaciones": "Tomar después de comer"
    }


# =========================
# PRUEBAS DE VALIDACIONES
# =========================

def test_validar_medicamento_exitoso():
    data = medicamento_valido()
    errores = validar_medicamento(data)
    assert errores == []


def test_nombre_medicamento_vacio():
    data = medicamento_valido()
    data["nombre_medicamento"] = ""
    errores = validar_medicamento(data)
    assert "El nombre del medicamento es obligatorio" in errores


def test_dosis_vacia():
    data = medicamento_valido()
    data["dosis_cantidad"] = ""
    errores = validar_medicamento(data)
    assert "La dosis es obligatoria" in errores


def test_frecuencia_vacia():
    data = medicamento_valido()
    data["frecuencia"] = ""
    errores = validar_medicamento(data)
    assert "La frecuencia es obligatoria" in errores


def test_horario_vacio():
    data = medicamento_valido()
    data["horarios"] = []
    errores = validar_medicamento(data)
    assert "Debe ingresar al menos un horario" in errores


def test_fecha_inicio_vacia():
    data = medicamento_valido()
    data["fecha_inicio"] = ""
    errores = validar_medicamento(data)
    assert "La fecha de inicio es obligatoria" in errores


def test_paciente_id_faltante():
    data = medicamento_valido()
    del data["paciente_id"]
    errores = validar_medicamento(data)
    assert "El paciente_id es obligatorio" in errores


def test_paciente_id_invalido_texto():
    data = medicamento_valido()
    data["paciente_id"] = "abc"
    errores = validar_medicamento(data)
    assert "El paciente_id debe ser un número entero válido" in errores


def test_paciente_id_invalido_menor_o_igual_a_cero():
    data = medicamento_valido()
    data["paciente_id"] = 0
    errores = validar_medicamento(data)
    assert "El paciente_id debe ser un número mayor que 0" in errores


# =========================
# PRUEBAS DE BASE DE DATOS
# =========================

def test_verificar_paciente_existe_devuelve_true():
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
        "Ana", "Lopez", "01/15/1990", "Femenino",
        "CC", "12345678", "3001234567", "Sura", "Hipertension"
    ))

    conn.commit()

    resultado = verificar_paciente_existe(1, conn)

    assert resultado is True
    conn.close()


def test_verificar_paciente_existe_devuelve_false():
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

    resultado = verificar_paciente_existe(99, conn)

    assert resultado is False
    conn.close()


def test_verificar_medicamento_duplicado_devuelve_true():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT NOT NULL,
            frecuencia TEXT NOT NULL,
            horario TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            observaciones TEXT,
            paciente_id INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario,
            fecha_inicio, observaciones, paciente_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Acetaminofen", "1 tableta", "Cada 8 horas", "08:00, 16:00, 00:00",
        "03/16/2026", "Concentración: 500 mg | Forma farmacéutica: Tableta", 1
    ))

    conn.commit()

    resultado = verificar_medicamento_duplicado("Acetaminofen", 1, conn)

    assert resultado is True
    conn.close()


def test_verificar_medicamento_duplicado_devuelve_false():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT NOT NULL,
            frecuencia TEXT NOT NULL,
            horario TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            observaciones TEXT,
            paciente_id INTEGER NOT NULL
        )
    """)

    conn.commit()

    resultado = verificar_medicamento_duplicado("Ibuprofeno", 1, conn)

    assert resultado is False
    conn.close()


# =========================
# PRUEBAS DEL ENDPOINT
# =========================

def test_post_medicamento_exitoso():
    data = medicamento_valido()

    conexion_falsa = MagicMock()
    cursor_falso = MagicMock()
    conexion_falsa.cursor.return_value = cursor_falso

    with patch("backend.routes.medication_route.sqlite3.connect", return_value=conexion_falsa), \
         patch("backend.routes.medication_route.verificar_paciente_existe", return_value=True), \
         patch("backend.routes.medication_route.verificar_medicamento_duplicado", return_value=False):

        response = client.post("/medicamentos/", json=data)

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Medicamento registrado existosamente"


def test_post_medicamento_datos_invalidos():
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    response = client.post("/medicamentos/", json=data)

    assert response.status_code == 400
    assert "El nombre del medicamento es obligatorio" in response.json()["detail"]


def test_post_medicamento_paciente_no_existe():
    data = medicamento_valido()

    conexion_falsa = MagicMock()

    with patch("backend.routes.medication_route.sqlite3.connect", return_value=conexion_falsa), \
         patch("backend.routes.medication_route.verificar_paciente_existe", return_value=False):

        response = client.post("/medicamentos/", json=data)

    assert response.status_code == 404
    assert response.json()["detail"] == "El paciente no existe"


def test_post_medicamento_duplicado():
    data = medicamento_valido()

    conexion_falsa = MagicMock()

    with patch("backend.routes.medication_route.sqlite3.connect", return_value=conexion_falsa), \
         patch("backend.routes.medication_route.verificar_paciente_existe", return_value=True), \
         patch("backend.routes.medication_route.verificar_medicamento_duplicado", return_value=True):

        response = client.post("/medicamentos/", json=data)

    assert response.status_code == 400
    assert response.json()["detail"] == "El paciente ya tiene registrado este medicamento"