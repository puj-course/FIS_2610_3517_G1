from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

def guardar_alerta(tipo, mensaje, severidad, paciente_id, medicamento_id=None, recordatorio_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO alertas (
            tipo,
            mensaje,
            severidad,
            paciente_id,
            medicamento_id,
            recordatorio_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (tipo, mensaje, severidad, paciente_id, medicamento_id, recordatorio_id)
    )

    conn.commit()
    conn.close()