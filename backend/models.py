import os
import sqlite3
from datetime import datetime

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            severidad TEXT NOT NULL,
            paciente_id INTEGER NOT NULL,
            medicamento_id INTEGER,
            recordatorio_id INTEGER,
            fecha_creacion TEXT NOT NULL,
            atendida INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
            FOREIGN KEY (recordatorio_id) REFERENCES recordatorios(id)
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


def get_recordatorios_activos(medicamento_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM recordatorios
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


def get_panel_dia_por_paciente(paciente_id):
    conn = get_connection()
    cursor = conn.cursor()

    hoy = datetime.now()
    fecha_hoy = hoy.strftime("%m/%d/%Y")
    fecha_sql_hoy = hoy.strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT
            r.id AS recordatorio_id,
            m.paciente_id AS paciente_id,
            r.medicamento_id AS medicamento_id,
            m.nombre AS medicamento_nombre,
            m.dosis AS dosis,
            r.hora_recordatorio AS hora_recordatorio,
            r.fecha_inicio AS fecha_inicio,
            r.activo AS activo,
            r.observaciones AS observaciones,
            (? || ' ' || r.hora_recordatorio || ':00') AS fecha_programada,
            t.id AS toma_id,
            t.fecha_hora_toma AS fecha_hora_toma,
            t.estado AS estado_toma,
            CASE
                WHEN t.id IS NOT NULL THEN 1
                ELSE 0
            END AS tomada
        FROM recordatorios r
        INNER JOIN medicamentos m
            ON r.medicamento_id = m.id
        LEFT JOIN tomas_medicamento t
            ON t.recordatorio_id = r.id
           AND t.fecha_programada = (? || ' ' || r.hora_recordatorio || ':00')
        WHERE m.paciente_id = ?
          AND r.activo = 1
          AND r.fecha_inicio <= ?
        ORDER BY r.hora_recordatorio ASC
    """, (
        fecha_sql_hoy,
        fecha_sql_hoy,
        paciente_id,
        fecha_hoy
    ))

    filas = cursor.fetchall()
    conn.close()
    return filas


def obtener_historial_tomas(paciente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            t.id,
            t.paciente_id,
            t.medicamento_id,
            m.nombre AS medicamento_nombre,
            t.recordatorio_id,
            t.fecha_programada,
            t.fecha_hora_toma,
            t.estado,
            t.observaciones
        FROM tomas_medicamento t
        INNER JOIN medicamentos m
            ON t.medicamento_id = m.id
        WHERE t.paciente_id = ?
        ORDER BY t.fecha_programada DESC, t.fecha_hora_toma DESC
    """, (paciente_id,))

    resultados = cursor.fetchall()
    conn.close()
    return resultados


if __name__ == "__main__":
    init_db()
