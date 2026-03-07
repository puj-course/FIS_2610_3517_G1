from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from backend.auth import hash_password, verify_password_hash
from backend.models import get_connection

# Aquí se crea la instancia principal de la aplicación.
# Esta app es la que registra rutas/endpoints y gestiona las peticiones HTTP
app = FastAPI()

# Cuando llega una petición, FastAPI usa este modelo para validar
# que existan username y password y que ambos sean strings
class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/signin")
# Define una función asíncrona que manejará la petición de inicio de sesión
async def login_user(user_data: UserCreate):
    username = user_data.username
    password = user_data.password

    # Busca el usuario en la base de datos por correo
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT contrasena FROM usuarios WHERE correo = '{username}'")
    usuario = cursor.fetchone()
    conn.close()

    # Si no existe el usuario o la contraseña no coincide, lanza 401
    if not usuario or not verify_password_hash(password, usuario["contrasena"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    return {"detail": "Inicio de sesión exitoso"}


@app.post("/signup")
# Registra el endpoint HTTP POST /signup para registro de usuarios
async def create_user(user_data: UserCreate):
    username = user_data.username
    password = user_data.password

    conn = get_connection()
    cursor = conn.cursor()

    # Verifica si el correo ya está registrado
    cursor.execute(f"SELECT id FROM usuarios WHERE correo = '{username}'")
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")

    # Guarda el usuario con la contraseña hasheada
    hashed = hash_password(password)
    cursor.execute(f"INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES ('Usuario', '{username}', '{hashed}', 'cuidador')")
    conn.commit()
    conn.close()

    return {"detail": "Usuario creado exitosamente"}