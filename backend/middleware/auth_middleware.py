# auth_middleware.py
import os
import jwt

from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.authentication import AuthenticationError
from starlette.authentication import BaseUser
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    SimpleUser,
    UnauthenticatedUser,
)


unauthenticated_endpoints = [
    "/signup",
    "/signin",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/docs/oauth2-redirect",
]


class CustomUser(BaseUser):
    def __init__(self, username: str, roles: list = None):
        self.username = username
        self.roles = roles or []

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


def auth_error_handler(conn: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)}
    )


class BearerAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        route = conn.scope.get("path", "")
        method = conn.scope.get("method", "")

        if route in unauthenticated_endpoints or method == "OPTIONS":
            return AuthCredentials(["public"]), SimpleUser("public")

        auth_header = conn.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Solicitud No Autenticada.")

        token = auth_header.split(" ")[1]
        decoded_token = self.validate_token(token)

        if decoded_token:
            user = CustomUser(
                username=decoded_token.get("sub"),
                roles=[decoded_token.get("rol")]
            )
            return AuthCredentials([decoded_token.get("rol")]), user

        return AuthCredentials([]), UnauthenticatedUser()

    def validate_token(self, token):
        try:
            decoded = jwt.decode(
                token,
                os.getenv("SECRET_KEY"),
                algorithms=["HS256"]
            )
            return decoded

        except (jwt.InvalidSignatureError, jwt.exceptions.DecodeError):
            raise AuthenticationError("Token Invalido")

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token Expirado")