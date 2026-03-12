import os
<<<<<<< HEAD
# libreia liviana que estamos usando
=======
>>>>>>> develop
import sqlite3

# Esto asegura que la BD siempre quede en backend/database.db
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

<<<<<<< HEAD
# Funcion para abrir una conexión con la BD
=======
>>>>>>> develop
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

<<<<<<< HEAD
# Funcion para inicializar la BD
=======
>>>>>>> develop
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

<<<<<<< HEAD
    # Tabla de usuarios
=======
>>>>>>> develop
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('cuidador', 'administrador'))
        )
    """)

<<<<<<< HEAD
    # Tabla de pacientes
=======
>>>>>>> develop
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
<<<<<<< HEAD
            fecha_nacimiento TEXT NOT NULL,
=======
            fecha_nacimiento TEXT NOT NULL, -- mm/dd/yyyy
>>>>>>> develop
            genero TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            telefono_contacto TEXT NOT NULL,
<<<<<<< HEAD
            eps_aseguradora TEXT NOT NULL,
            diagnostico_principal TEXT NOT NULL,
            alergias_conocidas TEXT DEFAULT '',
            observaciones_adicionales TEXT DEFAULT '',
            UNIQUE(tipo_documento, numero_documento)
=======
            eps_aseguradora TEXT,
            diagnostico_principal TEXT,
            alergias_conocidas TEXT,
            observaciones_adicionales TEXT,
            UNIQUE (tipo_documento, numero_documento)
>>>>>>> develop
        )
    """)

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

    