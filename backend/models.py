import os
#Esta es una libreria de datos liviana que guarda todo en un .db
import sqlite3

# Esto asegura que la BD siempre quede en backend/database.db
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

#Funcion para abrir una conexi'on con la BD
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    #Para poder acceder a columnas por nombre
    conn.row_factory = sqlite3.Row
    return conn
#Funcion para inicializar la BD
def init_db():
    conn = get_connection()
    #cursor es el objeto que ejecuta sentencias de SQL, ej: CREATE, INSERT, SELECT
    cursor = conn.cursor()

    #Se crea la tabla si no existe con atributos, tambien se especifica la llave primaria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('cuidador', 'administrador'))
        )
    """)
    #Se guardan los cambios con un commit
    conn.commit()
    #Liberar recursos
    conn.close()
    #Se imprime por pantalla una confirmacion
    print("Base de datos inicializada correctamente.")
#Para ejecutar solo si se corre el archivo directamente
if __name__ == "__main__":
    init_db()

