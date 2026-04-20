from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models import init_db

from backend.routes.auth_route import router as auth_router
from backend.routes.patient_route import router as patient_router
from backend.routes.medication_route import router as medication_router
from backend.routes.recordatorio_route import router as recordatorio_router
from backend.routes.toma_route import router as toma_router
from backend.routes.historial_route import router as historial_router

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(medication_router)
app.include_router(recordatorio_router)
app.include_router(toma_router)
app.include_router(historial_router)