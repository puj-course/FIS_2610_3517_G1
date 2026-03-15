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
   # solo 2 subissues estan aqui
    # Tabla de pacientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL, -- mm/dd/yyyy
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

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")


if __name__ == "__main__":
    init_db()
    # aumentara la implementacion
    

