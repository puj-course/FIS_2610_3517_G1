# Subissue - Encriptar contraseñas

import hashlib
import jwt
from datetime import datetime, timedelta, timezone

"""
Módulo de autenticación para la aplicación.
Proporciona funciones para hash de contraseñas y generación/verificación de JWT.
"""

SECRET_KEY = "PLACEHOLDER"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando SHA-256 con un salt fijo.
    """
    salt = b"some_salt"
    pwd_salt = password + salt.decode("utf-8")
    digest = hashlib.sha256(pwd_salt.encode("utf-8"))
    return digest.hexdigest()


def verify_password_hash(password: str, reference_hash: str) -> bool:
    """
    Compara la contraseña ingresada con el hash almacenado.
    """
    return hash_password(password) == reference_hash


def generate_jwt(user_id: int, correo: str, rol: str) -> str:
    """
    Genera un JWT firmado con datos básicos del usuario.
    """
    now = datetime.now(timezone.utc)

    payload = {
        "iss": "MedTrack",
        "sub": correo,
        "id": user_id,
        "rol": rol,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=8)).timestamp()),
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt(token: str):
    """
    Verifica y decodifica un JWT.
    Retorna el payload si es válido, o None si no lo es.
    """
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None