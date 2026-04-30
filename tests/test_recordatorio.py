from backend.models import get_connection


def test_crear_recordatorio():
    conn = get_connection()
    cursor = conn.cursor()

    # PACIENTE
    cursor.execute("""
        INSERT INTO pacientes (
            nombres, apellidos, fecha_nacimiento, genero,
            tipo_documento, numero_documento, telefono_contacto
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Test",
        "Paciente",
        "1990-01-01",
        "F",
        "CC",
        "123456",
        "3001234567"
    ))

    paciente_id = cursor.lastrowid

    # MEDICAMENTO
    cursor.execute("""
        INSERT INTO medicamentos 
        (nombre, dosis, frecuencia, horario, fecha_inicio, paciente_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Aspirina',
        '500mg',
        'diaria',
        'mañana',
        '2024-01-01',
        paciente_id
    ))

    medicamento_id = cursor.lastrowid

    #RECORDATORIO
    cursor.execute("""
        INSERT INTO recordatorios 
        (medicamento_id, hora_recordatorio, fecha_inicio, activo, observaciones)
        VALUES (?, ?, ?, ?, ?)
    """, (
        medicamento_id,
        '08:00',
        '2024-01-01',
        1,
        'Tomar con comida'
    ))

    conn.commit()

    # VALIDACIÓN
    cursor.execute("""
        SELECT * FROM recordatorios WHERE medicamento_id = ?
    """, (medicamento_id,))

    recordatorio = cursor.fetchone()

    conn.close()

    assert recordatorio is not None
    assert recordatorio["medicamento_id"] == medicamento_id
    assert recordatorio["hora_recordatorio"] == '08:00'
    assert recordatorio["activo"] == 1