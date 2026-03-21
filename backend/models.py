import os
import sqlite3

# Esto asegura que la BD siempre quede en backend/database.db
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

# Funcion para abrir una conexión con la BD
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Funcion para inicializar la BD
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('cuidador', 'administrador'))
        )
    """)

    # Tabla de pacientes
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

    # Tabla de medicamentos
    # Campos obligatorios: nombre, dosis, frecuencia, horario, fecha_inicio, paciente_id
    # Campo opcional: observaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicamentos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre           TEXT    NOT NULL,
            dosis            TEXT    NOT NULL,
            frecuencia       TEXT    NOT NULL,
            horario          TEXT    NOT NULL,
            fecha_inicio     TEXT    NOT NULL,
            observaciones    TEXT,
            paciente_id      INTEGER NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)
    

    # Tabla de recordatorios
    # Campos: id, medicamento_id (FK), hora (HH:MM), dias (texto separado por comas), activo (0 o 1)
    # Relacion: cada recordatorio pertenece a un medicamento registrado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordatorios (
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordatorios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id  INTEGER NOT NULL,
            hora            TEXT    NOT NULL,
            dias            TEXT    NOT NULL,
            activo          INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
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

    recordatorios = cursor.fetchall()
    conn.close()
    return recordatorios

def insertar_recordatorio(medicamento_id, hora, dias, activo=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recordatorios (medicamento_id, hora, dias, activo)
        VALUES (?, ?, ?, ?)
    """, (medicamento_id, hora, dias, activo))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    # aumentara la implementacion

if __name__ == "__main__":
    init_db()
    # aumentara la implementacion