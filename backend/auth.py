<<<<<<< HEAD
# Subissue - Encriptar contraseñas
#import section 
import cryptography
=======
# Subissue - Encriptar contraseñas
#import section 
import hashlib
import jwt
from datetime import datetime, timedelta, timezone

"""
Módulo de autenticación para la aplicación

Proporciona funciones para el hash de contraseñas, generación y verificación de JWTs.
"""

# Global variables
SECRET_KEY="PLACEHOLDER"
ALGORITHM = 'HS256'

def hash_password(password): #firma de la función

    salt        =   b'some_salt' #salt para agregar seguridad a la contraseña
    
    pwd_salt    =   password+salt.decode("utf-8")  

    digest      =   hashlib.sha256(pwd_salt.encode())

    return digest.hexdigest()


def verify_password_hash(password, reference_hash):

    return hash_password(password) == reference_hash

def generate_jwt():

    payload = {
        'iss': 'PLACEHOLDER',
        'sub': 'PLACEHOLDER',
        'iat': int((datetime.now(timezone.utc)).timestamp()),
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=0.5)).timestamp()),
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_jwt(token):
    try:

        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decoded_jwt
    
    except jwt.ExpiredSignatureError:

        print("Token has expired")
        return None
    
    except jwt.InvalidTokenError:

        print("Invalid token")
        return None
    
>>>>>>> develop
