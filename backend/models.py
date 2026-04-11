import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('cuidador', 'administrador'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
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
            observaciones_adicionales TEXT,
            UNIQUE (tipo_documento, numero_documento)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT NOT NULL,
            frecuencia TEXT NOT NULL,
            horario TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            observaciones TEXT,
            paciente_id INTEGER NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Tabla de recordatorios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL,
            hora_recordatorio TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            observaciones TEXT,
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
        )
    """)

    # Tabla de tomas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_programada TEXT NOT NULL,
            hora_tomada TEXT,
            estado TEXT NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'tomado', 'atrasado')),
            observaciones TEXT,
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")


def get_recordatorios_activos(medicamento_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM recordatorios
        WHERE medicamento_id = ? AND activo = 1
    """, (medicamento_id,))
    recordatorios = cursor.fetchall()
    conn.close()
    return recordatorios


def insertar_recordatorio(medicamento_id, hora_recordatorio, fecha_inicio, activo=1, observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recordatorios (
            medicamento_id, hora_recordatorio, fecha_inicio, activo, observaciones
        )
        VALUES (?, ?, ?, ?, ?)
    """, (medicamento_id, hora_recordatorio, fecha_inicio, activo, observaciones))
    conn.commit()
    conn.close()


def obtener_historial_tomas(paciente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            t.id,
            t.paciente_id,
            t.medicamento_id,
            m.nombre,
            t.fecha,
            t.hora_programada,
            t.hora_tomada,
            t.estado,
            t.observaciones
        FROM tomas t
        JOIN medicamentos m ON t.medicamento_id = m.id
        WHERE t.paciente_id = ?
        ORDER BY t.fecha DESC, t.hora_programada DESC
    """, (paciente_id,))

    resultados = cursor.fetchall()
    conn.close()

    return resultados


if __name__ == "__main__":
    init_db()