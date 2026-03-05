from fastapi            import FastAPI, status, HTTPException
from pydantic           import BaseModel
from backend.auth       import hash_password

#Aquí se crea la instancia principal de la aplicación. Esta app es la que registra rutas-endpoints y gestiona las peticiones HTTP
app = FastAPI()

#Cuando llega una petición, FastAPI usa el siguiente modeo para validar que exista el nombre de usuario, la contraseña y validar que ambos sean strings
class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/signin")
# (asyn def...)Define una función asíncrona que manejará la petición
async def login_user(user_data: UserCreate):
    #Extraer username y passworf del request
    username = user_data.username
    
    password = user_data.password

    ##PLACEHOLDER - Lógica para almacenar el usuario en la base de datos
    #Validacion temporal de credenciales
    if username == "testuser" and hash_password(password) == hash_password("testpassword"): #TODO: Reemplazar esta lógica con la verificación real de la base de datos

        return {
            "detail": "Successfully logged in",
        }
    
    else:
     # Si las credenciales no coinciden, se lanza una respuesta HTTP 401 Unauthorized
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@app.post("/signup")
# Registra el endpoint HTTP POST /signup para alta/registro de usuarios
# FastAPI valida el body con UserCreate antes de ejecutar la lógica del endpoint

async def create_user(user_data: UserCreate):

    username = user_data.username
    
    password = user_data.password

    ##PLACEHOLDER - Lógica para almacenar el usuario en la base de datos

    return {
        "detail": "User created successfully",
        "username": username,
        "hashed_password": hash_password(password)  #TODO: Eliminar esta línea después de verificar que el hash se genera correctamente
    }