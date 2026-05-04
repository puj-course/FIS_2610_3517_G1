from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

from backend.auth import hash_password, verify_password_hash, generate_jwt
from backend.database import usuarios_col

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    nombre: str
    username: str
    password: str
    rol: str


@router.post("/signin")
async def login_user(user_data: UserCreate):
    usuario = usuarios_col.find_one({"correo": user_data.username})

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    if not verify_password_hash(user_data.password, usuario["contrasena"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    token = generate_jwt(str(usuario["_id"]), usuario["correo"], usuario["rol"])

    return {
        "detail": "Inicio de sesión exitoso",
        "token": token,
        "usuario": {
            "id": str(usuario["_id"]),
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
            "rol": usuario["rol"]
        }
    }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserRegister):

    if user_data.rol not in ("cuidador", "administrador"):
        raise HTTPException(status_code=400, detail="Rol inválido.")

    if usuarios_col.find_one({"correo": user_data.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )

    hashed = hash_password(user_data.password)

    usuarios_col.insert_one({
        "nombre": user_data.nombre,
        "correo": user_data.username,
        "contrasena": hashed,
        "rol": user_data.rol
    })

    return {"detail": "Usuario creado exitosamente"}