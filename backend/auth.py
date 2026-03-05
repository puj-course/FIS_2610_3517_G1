# Subissue - Encriptar contraseñas
# import section
import hashlib
import jwt
from datetime import datetime, timedelta, timezone

"""
Módulo de autenticación para la aplicación 
Proporciona funciones para el hash de contraseñas, generación y verificación de JWTs,
es decir, este módulo existe para proteger contraseñas con hash y manejar autenticación con JWT.
"""

# Variable Global
SECRET_KEY = "PLACEHOLDER"

# Algoritmo de firma
ALGORITHM = 'HS256'

# Esta funcion toma la contraseña, le agrega un salt (evita que dos contraseñas iguales tengan el mismo hash),
# posteriormente calcula el SHA-256 y finalmente devuelve el hash en formato hexadecimal
def hash_password(password):
    salt     = b'some_salt'  # salt para agregar seguridad a la contraseña
    pwd_salt = password + salt.decode("utf-8")  # así el hash no depende solo de la contraseña original
    digest   = hashlib.sha256(pwd_salt.encode())
    return digest.hexdigest()  # hexdigest es más sencillo de guardar en BD (TEXT) y comparar

# Funcion que hashea la contraseña que el usuario escribió y la compara con el hash guardado
def verify_password_hash(password, reference_hash):
    return hash_password(password) == reference_hash

# Funcion que crea un payload y lo firma
def generate_jwt():
    payload = {
        'iss': 'PLACEHOLDER',  # para identificar el sistema emisor
        'sub': 'PLACEHOLDER',  # un token representa un usuario
        'iat': int((datetime.now(timezone.utc)).timestamp()),  # momento de emisión
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=0.5)).timestamp()),  # momento de expiración
    }
    # Si alguien modifica el payload, la firma deja de ser válida
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# El objetivo de esta función es devolver el payload decodificado
def verify_jwt(token):
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decoded_jwt
    # Validación de seguridad relacionada a sesión vencida
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    # Protege contra tokens mal construidos
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None  # no rompemos el programa