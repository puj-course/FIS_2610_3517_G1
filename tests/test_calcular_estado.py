# backend/tests/test_calcular_estado.py

from datetime import datetime
from backend.states.estado_toma import calcular_estado

# Medicamento de prueba reutilizable 
MEDICAMENTO = {"id": 1, "horario": "08:00"}

def test_estado_tomado():
    tomas = [{"medicamento_id": 1, "estado": "tomado"}]
    hora_actual = datetime.now().replace(hour=9, minute=0)
    resultado = calcular_estado(MEDICAMENTO, hora_actual, tomas)
    assert resultado == "tomado"

def test_estado_atrasado():
    hora_actual = datetime.now().replace(hour=10, minute=30)  # 2.5h después
    resultado = calcular_estado(MEDICAMENTO, hora_actual, [])
    assert resultado == "atrasado"

def test_estado_pendiente():
    hora_actual = datetime.now().replace(hour=8, minute=20)  # solo 20 min
    resultado = calcular_estado(MEDICAMENTO, hora_actual, [])
    assert resultado == "pendiente"

def test_hora_malformada():
    med_roto = {"id": 2, "horario": "hora_invalida"}
    hora_actual = datetime.now().replace(hour=9, minute=0)
    resultado = calcular_estado(med_roto, hora_actual, [])
    assert resultado == "pendiente"  # el except ValueError devuelve pendiente