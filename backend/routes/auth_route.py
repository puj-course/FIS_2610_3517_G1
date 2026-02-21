from fastapi            import FastAPI, status, HTTPException
from pydantic           import BaseModel
from backend.auth       import hash_password

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/signin")
async def login_user(user_data: UserCreate):

    username = user_data.username
    
    password = user_data.password

    ##PLACEHOLDER - Lógica para almacenar el usuario en la base de datos

    if username == "testuser" and hash_password(password) == hash_password("testpassword"): #TODO: Reemplazar esta lógica con la verificación real de la base de datos

        return {
            "detail": "Successfully logged in",
        }
    
    else:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@app.post("/signup")
async def create_user(user_data: UserCreate):

    username = user_data.username
    
    password = user_data.password

    ##PLACEHOLDER - Lógica para almacenar el usuario en la base de datos

    return {
        "detail": "User created successfully",
        "username": username,
        "hashed_password": hash_password(password)  #TODO: Eliminar esta línea después de verificar que el hash se genera correctamente
    }