import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise ValueError("Debes definir la variable de entorno MONGO_URI")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["MEDTRACK"]

usuarios_col      = db["usuarios"]
pacientes_col     = db["pacientes"]
medicamentos_col  = db["medicamentos"]
recordatorios_col = db["recordatorios"]
tomas_col         = db["tomas_medicamento"]
alertas_col       = db["alertas"]