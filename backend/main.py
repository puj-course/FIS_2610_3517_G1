# main.py del backend

from fastapi import FastAPI
from backend.routes.patient_route import router as patient_router
# from backend.routes.auth_route import router as auth_router

app = FastAPI()
app.include_router(patient_router)
# app.include_router(auth_router)
