from fastapi import FastAPI
from backend.models import init_db
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.auth_route import router as auth_router
from backend.routes.patient_route import router as patient_router
from backend.routes.medication_route import router as medication_router
from backend.routes.reminder_route import router as reminder_router
from backend.routes.toma_route import router as toma_router
from backend.routes.historial_route import router as historial_router 

app = FastAPI()


init_db()

# para que frontend se conecte al backend

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
app.include_router(reminder_router)
app.include_router(toma_router)
app.include_router(historial_router)
