import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_recordatorio, verificar_medicamento_existe
from backend.main import app

client = TestClient(app)


def recordatorio_valido():
    return {
        "medicamento_id": 1,
        "hora_recordatorio": "08:30",
        "fecha_inicio": "03/25/2026",
        "activo": 1,
        "observaciones": "Prueba"
    }


# =========================
# VALIDACIONES
# =========================

def test_validar_recordatorio_exitoso():
    data = recordatorio_valido()
    errores = validar_recordatorio(data)
    assert errores == []


def test_medicamento_id_faltante():
    data = recordatorio_valido()
    del data["medicamento_id"]
    errores = validar_recordatorio(data)
    assert "La id del medicamento es obligatoria" in errores


def test_hora_recordatorio_vacia():
    data = recordatorio_valido()
    data["hora_recordatorio"] = ""
    errores = validar_recordatorio(data)
    assert "Favor ingresar la hora del recordatorio" in errores


def test_fecha_inicio_vacia():
    data = recordatorio_valido()
    data["fecha_inicio"] = ""
    errores = validar_recordatorio(data)
    assert "Se requiere la fecha de inicio" in errores


def test_medicamento_id_invalido_texto():
    data = recordatorio_valido()
    data["medicamento_id"] = "abc"
    errores = validar_recordatorio(data)
    assert "La id del del medicamento debe ser un entero válido" in errores


def test_medicamento_id_invalido_menor_o_igual_a_cero():
    data = recordatorio_valido()
    data["medicamento_id"] = 0
    errores = validar_recordatorio(data)
    assert "La id del medicamento debe ser un número > 0" in errores


def test_hora_formato_invalido():
    data = recordatorio_valido()
    data["hora_recordatorio"] = "8pm"
    errores = validar_recordatorio(data)
    assert "La hora del recordatorio debe tener formato HH:MM" in errores


def test_fecha_inicio_formato_invalido():
    data = recordatorio_valido()
    data["fecha_inicio"] = "2026-03-25"
    errores = validar_recordatorio(data)
    assert "La fecha de inicio debe tener formato mm/dd/yyyy" in errores


def test_activo_invalido():
    data = recordatorio_valido()
    data["activo"] = 5
    errores = validar_recordatorio(data)
    assert "El campo activo debe ser 0 o 1" in errores


# =========================
# BASE DE DATOS
# =========================

def test_verificar_medicamento_existe_devuelve_true():
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
            nombre, dosis, frecuencia, horario, fecha_inicio, observaciones, paciente_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Acetaminofen", "500 mg", "Cada 8 horas", "08:00 AM",
        "03/16/2026", "Ninguna", 1
    ))

    conn.commit()

    resultado = verificar_medicamento_existe(1, conn)

    assert resultado is True
    conn.close()


def test_verificar_medicamento_existe_devuelve_false():
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

    resultado = verificar_medicamento_existe(99, conn)

    assert resultado is False
    conn.close()


# =========================
# ENDPOINT POST
# =========================

def test_post_recordatorio_exitoso():
    data = recordatorio_valido()

    conexion_falsa = MagicMock()

    with patch("backend.routes.reminder_route.sqlite3.connect", return_value=conexion_falsa), \
         patch("backend.routes.reminder_route.verificar_medicamento_existe", return_value=True), \
         patch("backend.routes.reminder_route.insertar_recordatorio", return_value=1):

        response = client.post("/recordatorios/", json=data)

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Recordatorio creado correctamente"
    assert response.json()["recordatorio_id"] == 1


def test_post_recordatorio_datos_invalidos():
    data = recordatorio_valido()
    data["hora_recordatorio"] = ""

    response = client.post("/recordatorios/", json=data)

    assert response.status_code == 400
    assert "Favor ingresar la hora del recordatorio" in response.json()["detail"]


def test_post_recordatorio_medicamento_no_existe():
    data = recordatorio_valido()

    conexion_falsa = MagicMock()

    with patch("backend.routes.reminder_route.sqlite3.connect", return_value=conexion_falsa), \
         patch("backend.routes.reminder_route.verificar_medicamento_existe", return_value=False):

        response = client.post("/recordatorios/", json=data)

    assert response.status_code == 404
    assert response.json()["detail"] == "El medicamento no existe"


# =========================
# ENDPOINT GET
# =========================

def test_get_recordatorios_paciente_no_encontrado():
    conexion_falsa = MagicMock()
    cursor_falso = MagicMock()

    cursor_falso.fetchone.return_value = None
    cursor_falso.fetchall.return_value = []

    conexion_falsa.cursor.return_value = cursor_falso

    with patch("backend.routes.reminder_route.sqlite3.connect", return_value=conexion_falsa):
        response = client.get("/recordatorios/1")

    assert response.status_code == 200
    assert response.json() == {"recordatorios": []}


def test_get_recordatorios_exitoso():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Tabla pacientes
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

    # Tabla medicamentos
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

    # Tabla recordatorios
    cursor.execute("""
        CREATE TABLE recordatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL,
            hora_recordatorio TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            observaciones TEXT
        )
    """)

    # Insertar paciente
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

    # Insertar medicamento
    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario, fecha_inicio, observaciones, paciente_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Acetaminofen", "500 mg", "Cada 8 horas", "08:00 AM",
        "03/16/2026", "Ninguna", 1
    ))

    # Insertar recordatorio
    cursor.execute("""
        INSERT INTO recordatorios (
            medicamento_id, hora_recordatorio, fecha_inicio, activo, observaciones
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        1, "08:30", "03/25/2026", 1, "Prueba"
    ))

    conn.commit()

    with patch("backend.routes.reminder_route.sqlite3.connect", return_value=conn):
        response = client.get("/recordatorios/1")

    assert response.status_code == 200
    cuerpo = response.json()
    assert "recordatorios" in cuerpo
    assert len(cuerpo["recordatorios"]) == 1
    assert cuerpo["recordatorios"][0]["medicamento_nombre"] == "Acetaminofen"
    assert cuerpo["recordatorios"][0]["hora_recordatorio"] == "08:30"

    conn.close()


def test_get_recordatorios_lista_vacia():
    conexion_falsa = MagicMock()
    cursor_falso = MagicMock()

    cursor_falso.fetchone.return_value = {"id": 1}
    cursor_falso.fetchall.return_value = []

    conexion_falsa.cursor.return_value = cursor_falso

    with patch("backend.routes.reminder_route.sqlite3.connect", return_value=conexion_falsa):
        response = client.get("/recordatorios/1")

    assert response.status_code == 200
    assert response.json() == {"recordatorios": []}