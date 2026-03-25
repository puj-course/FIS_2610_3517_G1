# main.py del backend

from fastapi import FastAPI
from backend.routes.patient_route import router as patient_router # Registro de patient_route

## Para el end point de medicamentos
from backend.routes.medication_route import router as medication_router

# para el endpoint de recordatorios
from backend.routes.reminder_route import router as reminder_router

app = FastAPI()


app.include_router(patient_router)
app.include_router(medication_router)
app.include_router(reminder_router)
