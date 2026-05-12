# Subissue - Encriptar contraseñas

import os
import secrets
import hashlib
import jwt

from datetime import datetime, timedelta, timezone

"""
Módulo de autenticación para la aplicación.
Proporciona funciones para el hash de contraseñas,
generación y verificación de JWTs.
"""

# Clave secreta para firmar los JWT
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)

# Algoritmo de firma
ALGORITHM = "HS256"


# Esta función toma la contraseña, le agrega un salt
# y posteriormente calcula el SHA-256
def hash_password(password):
    salt = b'some_salt'

    # así el hash no depende solo de la contraseña original
    pwd_salt = password + salt.decode("utf-8")

    digest = hashlib.sha256(pwd_salt.encode())

    # hexdigest es más sencillo de guardar en BD
    return digest.hexdigest()


# Función que compara la contraseña ingresada
# con el hash almacenado
def verify_password_hash(password, reference_hash):
    return hash_password(password) == reference_hash


# Función que crea y firma un JWT
def generate_jwt(user_id, correo, rol):
    payload = {
        'iss': 'MedTrack',
        'sub': correo,
        'id': user_id,
        'rol': rol,
        'iat': int(datetime.now(timezone.utc).timestamp()),
        'exp': int(
            (datetime.now(timezone.utc) + timedelta(hours=8)).timestamp()
        ),
    }

    encoded_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# Función que valida y decodifica un JWT
def verify_jwt(token):
    try:
        decoded_jwt = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return decoded_jwt

    # Validación de seguridad relacionada a sesión vencida
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None

    # Protege contra tokens mal construidos
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None