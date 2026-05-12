from datetime import date
import re

from bson import ObjectId

import backend.database as database_module
import backend.routes.medication_route as medication_route
import backend.routes.reminder_route as reminder_route


class CursorFalso(list):
    def sort(self, campo, direccion=1):
        reverse = direccion == -1
        return CursorFalso(
            sorted(self, key=lambda item: item.get(campo, ""), reverse=reverse)
        )


class ResultadoUpdateFalso:
    def __init__(self, matched_count=1, modified_count=1):
        self.matched_count = matched_count
        self.modified_count = modified_count


class ColeccionFalsa:
    def __init__(self, documentos=None, matched_count=1):
        self.documentos = documentos or []
        self.matched_count = matched_count

    def find(self, filtro=None):
        filtro = filtro or {}
        return CursorFalso([
            documento
            for documento in self.documentos
            if self._coincide(documento, filtro)
        ])

    def find_one(self, filtro=None):
        filtro = filtro or {}

        for documento in self.documentos:
            if self._coincide(documento, filtro):
                return documento

        return None

    def update_one(self, filtro, update):
        return ResultadoUpdateFalso(matched_count=self.matched_count)

    def _coincide(self, documento, filtro):
        for clave, esperado in filtro.items():
            actual = documento.get(clave)

            if isinstance(esperado, dict):
                if "$lte" in esperado:
                    if str(actual) > str(esperado["$lte"]):
                        return False

                if "$regex" in esperado:
                    patron = esperado["$regex"]
                    if not re.search(patron, str(actual)):
                        return False

                continue

            if clave == "_id":
                if str(actual) != str(esperado):
                    return False

            elif actual != esperado:
                return False

        return True


def test_medication_panel_completo_con_toma_registrada(monkeypatch):
    paciente_id = ObjectId()
    medicamento_id = ObjectId()
    hoy_iso = date.today().isoformat()

    pacientes = ColeccionFalsa([
        {
            "_id": paciente_id,
            "cuidador_id": "cuidador-1",
            "nombres": "Ana",
            "apellidos": "Lopez",
        }
    ])

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "paciente_id": str(paciente_id),
            "nombre": "Aspirina",
            "dosis": "500 mg",
            "horario": "08:00, 20:00",
            "fecha_inicio": "01/01/2020",
            "fecha_fin": "",
        }
    ])

    tomas = ColeccionFalsa([
        {
            "_id": ObjectId(),
            "medicamento_id": str(medicamento_id),
            "fecha_programada": f"{hoy_iso} 08:00:00",
            "estado": "tomada",
        }
    ])

    monkeypatch.setattr(medication_route, "pacientes_col", pacientes)
    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos)
    monkeypatch.setattr(database_module, "tomas_col", tomas)

    respuesta = medication_route.obtener_panel_completo({"id": "cuidador-1"})

    assert "panel" in respuesta
    assert len(respuesta["panel"]) == 1
    assert respuesta["panel"][0]["nombres"] == "Ana"
    assert len(respuesta["panel"][0]["medicamentos"]) == 2
    assert respuesta["panel"][0]["medicamentos"][0]["tomado"] is True


def test_medication_panel_completo_ignora_medicamento_vencido(monkeypatch):
    paciente_id = ObjectId()
    medicamento_id = ObjectId()

    pacientes = ColeccionFalsa([
        {
            "_id": paciente_id,
            "cuidador_id": "cuidador-1",
            "nombres": "Ana",
            "apellidos": "Lopez",
        }
    ])

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "paciente_id": str(paciente_id),
            "nombre": "Aspirina",
            "dosis": "500 mg",
            "horario": "08:00",
            "fecha_inicio": "01/01/2020",
            "fecha_fin": "01/01/2021",
        }
    ])

    monkeypatch.setattr(medication_route, "pacientes_col", pacientes)
    monkeypatch.setattr(medication_route, "medicamentos_col", medicamentos)
    monkeypatch.setattr(database_module, "tomas_col", ColeccionFalsa([]))

    respuesta = medication_route.obtener_panel_completo({"id": "cuidador-1"})

    assert respuesta == {"panel": []}


def test_reminder_panel_completo_con_medicamento_tomado(monkeypatch):
    paciente_id = ObjectId()
    medicamento_id = ObjectId()
    hoy_iso = date.today().isoformat()

    pacientes = ColeccionFalsa([
        {
            "_id": paciente_id,
            "cuidador_id": "cuidador-1",
            "nombres": "Carlos",
            "apellidos": "Rojas",
        }
    ])

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "paciente_id": str(paciente_id),
            "nombre": "Losartán",
            "dosis": "50 mg",
            "horario": "09:00",
            "fecha_inicio": "01/01/2020",
            "fecha_fin": "",
        }
    ])

    tomas = ColeccionFalsa([
        {
            "_id": ObjectId(),
            "medicamento_id": str(medicamento_id),
            "fecha_programada": f"{hoy_iso} 09:00:00",
            "estado": "a_tiempo",
        }
    ])

    monkeypatch.setattr(reminder_route, "pacientes_col", pacientes)
    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos)
    monkeypatch.setattr(reminder_route, "tomas_col", tomas)

    respuesta = reminder_route.obtener_panel_completo({"id": "cuidador-1"})

    assert len(respuesta["panel"]) == 1
    assert respuesta["panel"][0]["nombres"] == "Carlos"
    assert respuesta["panel"][0]["medicamentos"][0]["tomado"] is True


def test_reminder_panel_completo_ignora_fecha_inicio_invalida(monkeypatch):
    paciente_id = ObjectId()
    medicamento_id = ObjectId()

    pacientes = ColeccionFalsa([
        {
            "_id": paciente_id,
            "cuidador_id": "cuidador-1",
            "nombres": "Carlos",
            "apellidos": "Rojas",
        }
    ])

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "paciente_id": str(paciente_id),
            "nombre": "Losartán",
            "dosis": "50 mg",
            "horario": "09:00",
            "fecha_inicio": "fecha-invalida",
            "fecha_fin": "",
        }
    ])

    monkeypatch.setattr(reminder_route, "pacientes_col", pacientes)
    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos)
    monkeypatch.setattr(reminder_route, "tomas_col", ColeccionFalsa([]))

    respuesta = reminder_route.obtener_panel_completo({"id": "cuidador-1"})

    assert respuesta == {"panel": []}


def test_reminder_panel_dia_con_recordatorio(monkeypatch):
    paciente_id = ObjectId()
    medicamento_id = ObjectId()
    recordatorio_id = ObjectId()

    pacientes = ColeccionFalsa([
        {
            "_id": paciente_id,
            "cuidador_id": "cuidador-1",
            "nombres": "Laura",
            "apellidos": "Perez",
        }
    ])

    recordatorios = ColeccionFalsa([
        {
            "_id": recordatorio_id,
            "paciente_id": str(paciente_id),
            "medicamento_id": str(medicamento_id),
            "activo": 1,
            "fecha_inicio": "01/01/2020",
            "hora_recordatorio": "07:30",
            "tomado": False,
        }
    ])

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "nombre": "Metformina",
            "dosis": "850 mg",
        }
    ])

    monkeypatch.setattr(reminder_route, "pacientes_col", pacientes)
    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios)
    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos)

    respuesta = reminder_route.obtener_panel_dia({"id": "cuidador-1"})

    assert len(respuesta["panel"]) == 1
    assert respuesta["panel"][0]["medicamentos"][0]["medicamento"] == "Metformina"


def test_reminder_panel_dia_paciente(monkeypatch):
    paciente_id = str(ObjectId())
    medicamento_id = ObjectId()
    recordatorio_id = ObjectId()

    recordatorios = ColeccionFalsa([
        {
            "_id": recordatorio_id,
            "paciente_id": paciente_id,
            "medicamento_id": str(medicamento_id),
            "activo": 1,
            "fecha_inicio": "01/01/2020",
            "hora_recordatorio": "10:00",
            "tomado": False,
            "observaciones": "Tomar con agua",
        }
    ])

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "nombre": "Ibuprofeno",
            "dosis": "400 mg",
        }
    ])

    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios)
    monkeypatch.setattr(reminder_route, "medicamentos_col", medicamentos)

    respuesta = reminder_route.obtener_panel_dia_paciente(
        paciente_id,
        {"id": "cuidador-1"},
    )

    assert len(respuesta["recordatorios"]) == 1
    assert respuesta["recordatorios"][0]["medicamento_nombre"] == "Ibuprofeno"
    assert respuesta["recordatorios"][0]["observaciones"] == "Tomar con agua"


def test_reminder_serializar_recordatorio_sin_medicamento():
    recordatorio = {
        "_id": ObjectId(),
        "medicamento_id": "med-1",
        "paciente_id": "pac-1",
        "medicamento_nombre": "Nombre guardado",
        "dosis": "10 mg",
        "hora_recordatorio": "08:00",
        "fecha_inicio": "01/01/2020",
        "activo": 1,
        "observaciones": "Obs",
        "tomado": False,
    }

    serializado = reminder_route.serializar_recordatorio(recordatorio)

    assert serializado["medicamento_nombre"] == "Nombre guardado"
    assert serializado["dosis"] == "10 mg"
    assert serializado["tomado"] is False


def test_reminder_marcar_recordatorio_como_tomado_no_encontrado(monkeypatch):
    recordatorios = ColeccionFalsa([], matched_count=0)

    monkeypatch.setattr(reminder_route, "recordatorios_col", recordatorios)

    try:
        reminder_route.marcar_recordatorio_como_tomado(str(ObjectId()))
        assert False
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 404