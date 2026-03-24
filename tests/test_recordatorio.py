import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import sqlite3
import pytest
from models import get_connection, init_db

def test_crear_recordatorio():
    conn = get_connection()
    cursor = conn.cursor()

    # Insertar medicamento de prueba
    cursor.execute("""
        INSERT INTO medicamentos (nombre, dosis, frecuencia, horario, fecha_inicio, paciente_id)
        VALUES ('Aspirina', '500mg', 'diaria', 'mañana', '2024-01-01', 1)
    """)
    medicamento_id = cursor.lastrowid

    # Insertar recordatorio de prueba
    cursor.execute("""
        INSERT INTO recordatorios (medicamento_id, hora, dias, activo)
        VALUES (?, '08:00', 'lunes,martes', 1)
    """, (medicamento_id,))

    conn.commit()

    # Verificar que quedó guardado
    cursor.execute("SELECT * FROM recordatorios WHERE medicamento_id = ?", (medicamento_id,))
    recordatorio = cursor.fetchone()

    assert recordatorio is not None
    assert recordatorio["hora"] == "08:00"
    assert recordatorio["dias"] == "lunes,martes"
    assert recordatorio["activo"] == 1

    conn.close()