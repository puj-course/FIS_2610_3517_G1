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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        concentracion TEXT,
        forma_farmaceutica TEXT,
        dosis TEXT NOT NULL,
        dosis_cantidad REAL,
        dosis_unidad TEXT,
        frecuencia TEXT NOT NULL,
        relacion_comida TEXT,
        horario TEXT NOT NULL,
        dias TEXT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT,
        via_administracion TEXT,
        medico_receto TEXT,
        instrucciones TEXT,
        observaciones TEXT,
        paciente_id INTEGER NOT NULL,
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
    )
""")


    # Tabla de recordatorios

    # AUTOINCREMENT hace que el sistema de BD genere las id 
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

    # Table de tomas/administraciones de medicamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tomas_medicamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        medicamento_id INTEGER NOT NULL,
        recordatorio_id INTEGER,
        fecha_programada TEXT NOT NULL,
        fecha_hora_toma TEXT,
        estado TEXT NOT NULL DEFAULT 'tomado',
        observaciones TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
        FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
        FOREIGN KEY (recordatorio_id) REFERENCES recordatorios(id),
        UNIQUE (recordatorio_id, fecha_programada)
    )
    """)
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

def get_recordatorios_por_paciente(paciente_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            r.id,
            r.medicamento_id,
            m.nombre AS medicamento_nombre,
            m.dosis AS dosis,
            r.hora_recordatorio,
            r.fecha_inicio,
            r.activo,
            r.observaciones
        FROM recordatorios r
        INNER JOIN medicamentos m
            ON r.medicamento_id = m.id
        WHERE m.paciente_id = ?
        ORDER BY r.fecha_inicio ASC, r.hora_recordatorio ASC
    """, (paciente_id,))
    recordatorios = cursor.fetchall()
    conn.close()
    return recordatorios


def insertar_recordatorio(medicamento_id, hora_recordatorio, fecha_inicio, activo=1, observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recordatorios (
            medicamento_id,
            hora_recordatorio,
            fecha_inicio,
            activo,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        medicamento_id,
        hora_recordatorio,
        fecha_inicio,
        activo,
        observaciones
    ))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

if __name__ == "__main__":
    init_db()
    # aumentara la implementacion


