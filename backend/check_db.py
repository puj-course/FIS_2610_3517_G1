import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, nombres, apellidos, tipo_documento, numero_documento FROM pacientes")
rows = cursor.fetchall()

print("Pacientes guardados:")
for r in rows:
    print(r)

conn.close()
