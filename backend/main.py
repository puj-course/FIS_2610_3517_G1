from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 👇 IMPORTS CORREGIDOS
from backend.routes.auth_route import router as auth_router
from backend.routes.patient_route import router as patient_router
from backend.routes.medication_route import router as medication_router
from backend.routes.reminder_route import router as reminder_router
from backend.routes.toma_route import router as toma_router  # 👈 ESTE TE FALTABA

from backend.models import init_db

init_db()

app = FastAPI()

# CORS (frontend conexión)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 REGISTRAR TODAS LAS RUTAS
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(medication_router)
app.include_router(reminder_router)
app.include_router(toma_router)  # 👈 IMPORTANTE