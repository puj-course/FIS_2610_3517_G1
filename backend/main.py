from fastapi import FastAPI
from backend.routes.patient_route import router as patient_router
from backend.routes.medication_route import router as medication_router
from backend.routes.reminder_route import router as reminder_router

app = FastAPI()

app.include_router(patient_router)
app.include_router(medication_router)
app.include_router(reminder_router)
