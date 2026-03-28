# backend/seed.py - correr una sola vez para crear usuario de prueba
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import get_connection, init_db
from backend.auth import hash_password

init_db()

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, contrasena, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Sofia",
        "sofia@medtrack.com",
        hash_password("admin123"),
        "cuidador"
    ))
    conn.commit()
    print("Usuario de prueba creado.")
except Exception as e:
    print(f"Error (puede que ya exista): {e}")
finally:
    conn.close()