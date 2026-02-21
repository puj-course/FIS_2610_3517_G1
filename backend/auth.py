# Subissue - Encriptar contraseñas
#import section 
import hashlib
import jwt
from datetime import datetime, timedelta, timezone

"""
Módulo de autenticación para la aplicación

Proporciona funciones para el hash de contraseñas, generación y verificación de JWTs, es decir, este módulo existe para proteger contraseñas con hash y manejar autenticación con JWT.
"""

# Variable Global
SECRET_KEY="PLACEHOLDER"
#Algoritmo de firma
ALGORITHM = 'HS256'

# ESta funcion toma la contraseña, le agrga un salt (evita que dos contraseñas iguales tengan el mismo hash), posteriormente calcula el SHA-256 y finalmente se devuelve el hash en formato hexadecimal. 

def hash_password(password): #firma de la función

    salt        =   b'some_salt' #salt para agregar seguridad a la contraseña
    #Así el hash no depende solo de la contraseña original
    pwd_salt    =   password+salt.decode("utf-8")  

    digest      =   hashlib.sha256(pwd_salt.encode())
    #Usamos hexdigest porque es mas sencillo de guardar en BD (TEXT) y comparar
    return digest.hexdigest()

#Funcion que hashea la contraseña que el usuario escribió y la compara con el hash guardado
def verify_password_hash(password, reference_hash):

    return hash_password(password) == reference_hash
#Funcion que crea un payload y lo firma
def generate_jwt():

    payload = {
        'iss': 'PLACEHOLDER', #para identificar el sistema emisor
        'sub': 'PLACEHOLDER', # Un token representa un usuario
        'iat': int((datetime.now(timezone.utc)).timestamp()), # Momento de emision
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=0.5)).timestamp()), # momento de expiracion
    }
    #Si alguien modifica el payload, la firma deja de ser válida
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# El objetivo de esta función es devolver el payload decodificado
def verify_jwt(token):
    try:

        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decoded_jwt
    #Validacion de seguridad relacionada a sesión vencida
    except jwt.ExpiredSignatureError:

        print("Token has expired")
        return None
    #Protege contra tokens mal construidos
    except jwt.InvalidTokenError:

        print("Invalid token")
        #No rompemos el programa
        return None
    