from fastapi              import APIRouter, status, HTTPException
from pydantic             import BaseModel
from backend.auth import hash_password, verify_password_hash, generate_jwt
from backend.models       import get_connection

# Creamos el router en vez de una app separada.
# Esto permite que main.py lo registre y use el CORS que ya tiene configurado.
router = APIRouter()


# Modelo para el inicio de sesión (solo correo y contraseña)
class UserCreate(BaseModel):
    username: str
    password: str


# Modelo para el registro (todos los campos)
class UserRegister(BaseModel):
    nombre:   str
    username: str
    password: str
    rol:      str


@router.post("/signin")
async def login_user(user_data: UserCreate):
    username = user_data.username
    password = user_data.password

    # Buscamos el usuario en la base de datos por correo
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (username,))
    usuario = cursor.fetchone()

    # Si no existe el usuario o la contraseña no coincide, error 401
    if not usuario or not verify_password_hash(password, usuario["contrasena"]):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    conn.close()

    # Generamos el token JWT con los datos del usuario
    token = generate_jwt(usuario["id"], usuario["correo"], usuario["rol"])

    # Devolvemos el token y los datos del usuario al frontend
    return {
        "detail": "Inicio de sesión exitoso",
        "token":  token,
        "usuario": {
            "id":     usuario["id"],
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
            "rol":    usuario["rol"]
        }
    }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserRegister):
    nombre   = user_data.nombre
    username = user_data.username
    password = user_data.password
    rol      = user_data.rol

    # Validamos que el rol sea válido
    if rol not in ("cuidador", "administrador"):
        raise HTTPException(status_code=400, detail="Rol inválido.")

    conn   = get_connection()
    cursor = conn.cursor()

    # Verificamos si el correo ya está registrado
    cursor.execute("SELECT id FROM usuarios WHERE correo = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )

    # Guardamos el usuario con la contraseña hasheada
    hashed = hash_password(password)
    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (?, ?, ?, ?)",
        (nombre, username, hashed, rol)
    )
    conn.commit()
    conn.close()

    return {"detail": "Usuario creado exitosamente"}