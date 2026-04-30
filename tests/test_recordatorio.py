import sqlite3
from backend.models import get_connection


def test_crear_recordatorio():
    conn = get_connection()
    cursor = conn.cursor()

    # Insertar paciente de prueba (si no existe)
    cursor.execute("""
        INSERT INTO pacientes (nombres, apellidos)
        VALUES ('Test', 'Paciente')
    """)
    paciente_id = cursor.lastrowid

    # Insertar medicamento de prueba
    cursor.execute("""
        INSERT INTO medicamentos 
        (nombre, dosis, frecuencia, horario, fecha_inicio, paciente_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Aspirina', '500mg', 'diaria', 'mañana', '2024-01-01', paciente_id))
    
    medicamento_id = cursor.lastrowid

    # Insertar recordatorio con estructura CORRECTA
    cursor.execute("""
        INSERT INTO recordatorios 
        (medicamento_id, hora_recordatorio, fecha_inicio, activo, observaciones)
        VALUES (?, ?, ?, ?, ?)
    """, (medicamento_id, '08:00', '2024-01-01', 1, 'Tomar con comida'))

    conn.commit()

    # Verificar que se insertó correctamente
    cursor.execute("""
        SELECT * FROM recordatorios WHERE medicamento_id = ?
    """, (medicamento_id,))
    
    recordatorio = cursor.fetchone()

    conn.close()

    assert recordatorio is not None
    assert recordatorio["medicamento_id"] == medicamento_id
    assert recordatorio["hora_recordatorio"] == '08:00'
    assert recordatorio["activo"] == 1