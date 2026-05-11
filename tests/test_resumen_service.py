########################################################################################
# test_resumen_service.py
########################################################################################

from unittest.mock import MagicMock
from bson import ObjectId
import pytest

from backend.services import resumen_paciente_service as resumen_module
from backend.services.resumen_paciente_service import ResumenPacienteService


PACIENTE_ID = "69feaac76a52afc46ed40c52"
PACIENTE_ID_2 = "69feaac76a52afc46ed40c53"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
TOMA_ID_1 = ObjectId("69feb500322be070cd1c97d0")
TOMA_ID_2 = ObjectId("69feb500322be070cd1c97d1")


@pytest.fixture
def colecciones_mock(monkeypatch):
    pacientes_col = MagicMock()
    medicamentos_col = MagicMock()
    tomas_col = MagicMock()

    pacientes_col.find_one.return_value = {
        "_id": ObjectId(PACIENTE_ID),
        "nombres": "Ana",
        "apellidos": "Lopez",
        "fecha_nacimiento": "01/15/2000",
        "genero": "Femenino",
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension",
        "alergias_conocidas": "",
        "observaciones_adicionales": ""
    }

    cursor_meds = MagicMock()
    cursor_meds.sort.return_value = [
        {
            "_id": ObjectId(MEDICAMENTO_ID),
            "nombre": "Aspirina",
            "dosis": "500 mg",
            "frecuencia": "Cada 8 horas",
            "horario": "08:00",
            "fecha_inicio": "2026-04-01",
            "observaciones": "Con comida",
            "paciente_id": PACIENTE_ID
        }
    ]
    medicamentos_col.find.return_value = cursor_meds

    medicamentos_col.find_one.return_value = {
        "_id": ObjectId(MEDICAMENTO_ID),
        "nombre": "Aspirina",
        "dosis": "500 mg",
        "paciente_id": PACIENTE_ID
    }

    cursor_tomas = MagicMock()
    cursor_tomas.sort.return_value = [
        {
            "_id": TOMA_ID_1,
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": "recordatorio-1",
            "fecha_programada": "2026-04-12 08:00:00",
            "fecha_hora_toma": "2026-04-12 08:05:00",
            "diferencia_minutos": 5.0,
            "estado": "tomado",
            "observaciones": "Tomada correctamente",
        },
        {
            "_id": TOMA_ID_2,
            "paciente_id": PACIENTE_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "recordatorio_id": "recordatorio-2",
            "fecha_programada": "2026-04-13 08:00:00",
            "fecha_hora_toma": None,
            "diferencia_minutos": None,
            "estado": "pendiente",
            "observaciones": "Pendiente",
        },
    ]
    tomas_col.find.return_value = cursor_tomas

    monkeypatch.setattr(resumen_module, "pacientes_col", pacientes_col)
    monkeypatch.setattr(resumen_module, "medicamentos_col", medicamentos_col)
    monkeypatch.setattr(resumen_module, "tomas_col", tomas_col)

    return {
        "pacientes_col": pacientes_col,
        "medicamentos_col": medicamentos_col,
        "tomas_col": tomas_col
    }


def test_paciente_ok(colecciones_mock):
    service = ResumenPacienteService()

    paciente = service.obtener_paciente(PACIENTE_ID)

    assert paciente["id"] == PACIENTE_ID
    assert paciente["nombres"] == "Ana"
    assert paciente["apellidos"] == "Lopez"


def test_paciente_none(colecciones_mock):
    colecciones_mock["pacientes_col"].find_one.return_value = None

    service = ResumenPacienteService()
    paciente = service.obtener_paciente("69feaac76a52afc46ed40999")

    assert paciente is None


def test_paciente_id_invalido(colecciones_mock):
    colecciones_mock["pacientes_col"].find_one.return_value = None

    service = ResumenPacienteService()

    paciente = service.obtener_paciente("id-invalido")

    assert paciente is None


def test_medicamentos_ok(colecciones_mock):
    service = ResumenPacienteService()

    medicamentos = service.obtener_medicamentos_activos(PACIENTE_ID)

    assert len(medicamentos) == 1
    assert medicamentos[0]["id"] == MEDICAMENTO_ID
    assert medicamentos[0]["nombre"] == "Aspirina"
    assert medicamentos[0]["paciente_id"] == PACIENTE_ID


def test_medicamentos_vacio(colecciones_mock):
    cursor_vacio = MagicMock()
    cursor_vacio.sort.return_value = []
    colecciones_mock["medicamentos_col"].find.return_value = cursor_vacio

    service = ResumenPacienteService()
    medicamentos = service.obtener_medicamentos_activos("69feaac76a52afc46ed40999")

    assert medicamentos == []


def test_historial_ok(colecciones_mock):
    service = ResumenPacienteService()

    historial = service.obtener_historial_formateado(PACIENTE_ID)

    assert len(historial) == 2
    assert historial[0]["id"] == str(TOMA_ID_1)
    assert historial[0]["medicamento"] == "Aspirina"
    assert historial[0]["medicamento_nombre"] == "Aspirina"
    assert historial[0]["fecha"] == "2026-04-12"
    assert historial[0]["hora_programada"] == "08:00:00"
    assert historial[0]["hora_tomada"] == "08:05:00"
    assert historial[0]["estado"] == "tomado"
    assert historial[1]["estado"] == "pendiente"


def test_resumen_ok(colecciones_mock):
    service = ResumenPacienteService()

    resumen = service.construir_resumen(PACIENTE_ID)

    assert resumen["paciente"]["id"] == PACIENTE_ID
    assert resumen["paciente"]["nombres"] == "Ana"
    assert resumen["paciente"]["apellidos"] == "Lopez"

    assert len(resumen["medicamentos_activos"]) == 1
    assert resumen["medicamentos_activos"][0]["nombre"] == "Aspirina"

    assert len(resumen["historial"]) == 2
    assert resumen["cumplimiento"]["total_tomas"] == 2
    assert resumen["cumplimiento"]["tomas_realizadas"] == 1
    assert resumen["cumplimiento"]["porcentaje"] == 50.0

    assert len(resumen["alertas"]) == 1


def test_resumen_404(colecciones_mock):
    colecciones_mock["pacientes_col"].find_one.return_value = None

    service = ResumenPacienteService()

    with pytest.raises(LookupError, match="Paciente no encontrado"):
        service.construir_resumen("69feaac76a52afc46ed40999")


def test_resumen_vacio(colecciones_mock):
    colecciones_mock["pacientes_col"].find_one.return_value = {
        "_id": ObjectId(PACIENTE_ID_2),
        "nombres": "Carlos",
        "apellidos": "Perez",
        "fecha_nacimiento": "02/20/2000",
        "genero": "Masculino",
        "tipo_documento": "CC",
        "numero_documento": "87654321",
        "telefono_contacto": "3111234567",
        "eps_aseguradora": "Nueva EPS",
        "diagnostico_principal": "Diabetes",
        "alergias_conocidas": "",
        "observaciones_adicionales": ""
    }

    cursor_meds_vacio = MagicMock()
    cursor_meds_vacio.sort.return_value = []
    colecciones_mock["medicamentos_col"].find.return_value = cursor_meds_vacio

    cursor_tomas_vacio = MagicMock()
    cursor_tomas_vacio.sort.return_value = []
    colecciones_mock["tomas_col"].find.return_value = cursor_tomas_vacio

    service = ResumenPacienteService()
    resumen = service.construir_resumen(PACIENTE_ID_2)

    assert resumen["paciente"]["id"] == PACIENTE_ID_2
    assert resumen["paciente"]["nombres"] == "Carlos"
    assert resumen["medicamentos_activos"] == []
    assert resumen["historial"] == []
    assert resumen["cumplimiento"]["total_tomas"] == 0
    assert resumen["cumplimiento"]["porcentaje"] == 0
    assert resumen["alertas"] == []

