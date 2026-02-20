# backend/seed.py  ← correr una sola vez para crear usuario de prueba
from models import get_connection, init_db
from auth import encriptar_contrasena

init_db()

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, contrasena, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Admin Prueba",
        "admin@medtrack.com",
        encriptar_contrasena("admin123"),
        "administrador"
    ))
    conn.commit()
    print("Usuario de prueba creado.")
except Exception as e:
    print(f"Error (puede que ya exista): {e}")
finally:
    conn.close()