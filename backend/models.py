import os
import sqlite3

# Esto asegura que la BD siempre quede en backend/database.db
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


# Función para abrir una conexión con la BD
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Función para inicializar la BD
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
    # Esta tabla se usa por toma_repository.py y toma_route.py
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_programada TEXT NOT NULL,
            hora_tomada TEXT,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            observaciones TEXT,
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Tabla de historial de tomas
    # Esta tabla guarda el estado real calculado de cada toma:
    # a_tiempo, tarde u omitida.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_tomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medicamento_id INTEGER NOT NULL,
            recordatorio_id INTEGER,
            fecha_programada TEXT NOT NULL,
            fecha_hora_toma TEXT,
            diferencia_minutos INTEGER,
            estado TEXT NOT NULL CHECK(estado IN ('a_tiempo', 'tarde', 'omitida')),
            observaciones TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
            FOREIGN KEY (recordatorio_id) REFERENCES recordatorios(id)
        )
    """)

    # Tabla de alertas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            severidad TEXT NOT NULL,
            paciente_id INTEGER NOT NULL,
            medicamento_id INTEGER,
            recordatorio_id INTEGER,
            fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            atendida INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
            FOREIGN KEY (recordatorio_id) REFERENCES recordatorios(id)
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


def insertar_recordatorio(
    medicamento_id,
    hora_recordatorio,
    fecha_inicio,
    activo=1,
    observaciones=None
):
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
    conn.close()


if __name__ == "__main__":
    init_db()

def get_recordatorios_por_paciente(paciente_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                r.id,
                r.medicamento_id,
                m.nombre AS medicamento_nombre,
                m.dosis,
                r.hora_recordatorio,
                r.fecha_inicio,
                r.activo,
                r.observaciones
            FROM recordatorios r
            INNER JOIN medicamentos m
                ON r.medicamento_id = m.id
            WHERE m.paciente_id = ?
            ORDER BY r.hora_recordatorio ASC
        """, (paciente_id,))

        return cursor.fetchall()

    finally:
        conn.close()


def get_panel_dia_por_paciente(paciente_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                r.id AS recordatorio_id,
                m.id AS medicamento_id,
                m.nombre AS medicamento_nombre,
                m.dosis,
                r.hora_recordatorio,
                COALESCE(
                    CASE
                        WHEN t.estado IN ('tomada', 'a_tiempo', 'tarde') THEN 1
                        ELSE 0
                    END,
                    0
                ) AS tomada
            FROM recordatorios r
            INNER JOIN medicamentos m
                ON r.medicamento_id = m.id
            LEFT JOIN tomas t
                ON t.medicamento_id = m.id
                AND t.hora_programada = r.hora_recordatorio
                AND t.fecha = DATE('now')
            WHERE m.paciente_id = ?
              AND r.activo = 1
            ORDER BY r.hora_recordatorio ASC
        """, (paciente_id,))

        return cursor.fetchall()

    finally:
        conn.close()
