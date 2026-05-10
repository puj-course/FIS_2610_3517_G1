from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from backend.models import init_db
from backend.middleware.auth_middleware import BearerAuthBackend, auth_error_handler

# Importación de todas las  rutas
from backend.routes.auth_route import router as auth_router
from backend.routes.patient_route import router as patient_router
from backend.routes.medication_route import router as medication_router
from backend.routes.reminder_route import router as reminder_router
from backend.routes.toma_route import router as toma_router
from backend.routes.historial_route import router as historial_router
from backend.routes.resumen_route import router as resumen_router

#Inicialización de la base de datos
init_db()

app = FastAPI()

# Middleware de Autenticación (Tokens)
# Se añade primero para que la app sepa quién es el usuario
app.add_middleware(
    AuthenticationMiddleware,
    backend=BearerAuthBackend(),
    on_error=auth_error_handler
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Registro de Routers
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(medication_router)
app.include_router(reminder_router)
app.include_router(toma_router)
app.include_router(historial_router)
app.include_router(resumen_router)