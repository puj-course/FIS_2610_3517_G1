from bson import ObjectId

import backend.scheduler as scheduler_module
import backend.services.sms_service as sms_service


class ColeccionFalsa:
    def __init__(self, documentos=None):
        self.documentos = documentos or []

    def find(self, filtro=None):
        return self.documentos

    def find_one(self, filtro=None):
        filtro = filtro or {}

        for documento in self.documentos:
            coincide = True

            for clave, esperado in filtro.items():
                actual = documento.get(clave)

                if clave == "_id":
                    if str(actual) != str(esperado):
                        coincide = False
                        break

                elif isinstance(esperado, dict):
                    if "$regex" in esperado:
                        if not str(actual).startswith(
                            str(esperado["$regex"]).replace("^", "")
                        ):
                            coincide = False
                            break

                    if "$in" in esperado:
                        if actual not in esperado["$in"]:
                            coincide = False
                            break

                elif actual != esperado:
                    coincide = False
                    break

            if coincide:
                return documento

        return None


class FechaHoraFalsa:
    def __init__(self, hora=7, minuto=45):
        self.hour = hora
        self.minute = minuto

    def strftime(self, formato):
        if formato == "%Y-%m-%d":
            return "2026-05-12"
        return "2026-05-12"


class DateTimeFalso:
    @staticmethod
    def now():
        return FechaHoraFalsa(hora=7, minuto=45)


def test_enviar_sms_sin_variables_de_entorno_no_falla(monkeypatch):
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_FROM", raising=False)

    resultado = sms_service.enviar_sms("3001234567", "Mensaje de prueba")

    assert resultado is None


def test_enviar_sms_con_variables_envia_mensaje(monkeypatch):
    mensajes = []

    class MensajesFalsos:
        def create(self, body, from_, to):
            mensajes.append({
                "body": body,
                "from": from_,
                "to": to,
            })

    class ClienteFalso:
        def __init__(self, sid, token):
            self.sid = sid
            self.token = token
            self.messages = MensajesFalsos()

    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "sid-test")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token-test")
    monkeypatch.setenv("TWILIO_FROM", "+1000000000")
    monkeypatch.setattr(sms_service, "Client", ClienteFalso)

    resultado = sms_service.enviar_sms("3001234567", "Mensaje de prueba")

    assert resultado is None
    assert mensajes[0]["to"] == "3001234567"
    assert mensajes[0]["body"] == "Mensaje de prueba"


def test_enviar_sms_maneja_error_de_twilio(monkeypatch):
    class ClienteFalsoConError:
        def __init__(self, sid, token):
            raise RuntimeError("fallo twilio")

    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "sid-test")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token-test")
    monkeypatch.setenv("TWILIO_FROM", "+1000000000")
    monkeypatch.setattr(sms_service, "Client", ClienteFalsoConError)

    resultado = sms_service.enviar_sms("3001234567", "Mensaje de prueba")

    assert resultado is None


def test_verificar_tomas_envia_recordatorio_sms(monkeypatch):
    paciente_id = ObjectId()
    cuidador_id = ObjectId()
    medicamento_id = ObjectId()

    mensajes = []

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "paciente_id": str(paciente_id),
            "nombre": "Losartán",
            "horario": "08:00",
        }
    ])

    pacientes = ColeccionFalsa([
        {
            "_id": paciente_id,
            "nombres": "Ana",
            "apellidos": "Lopez",
            "cuidador_id": str(cuidador_id),
        }
    ])

    usuarios = ColeccionFalsa([
        {
            "_id": cuidador_id,
            "nombre": "Cuidador",
            "telefono": "3001234567",
        }
    ])

    tomas = ColeccionFalsa([])

    monkeypatch.setattr(scheduler_module, "datetime", DateTimeFalso)
    monkeypatch.setattr(scheduler_module, "medicamentos_col", medicamentos)
    monkeypatch.setattr(scheduler_module, "pacientes_col", pacientes)
    monkeypatch.setattr(scheduler_module, "usuarios_col", usuarios)
    monkeypatch.setattr(scheduler_module, "tomas_col", tomas)
    monkeypatch.setattr(scheduler_module, "ya_enviados", set())

    monkeypatch.setattr(
        scheduler_module,
        "enviar_sms",
        lambda telefono, mensaje: mensajes.append((telefono, mensaje)),
    )

    scheduler_module.verificar_tomas()

    assert len(mensajes) == 1
    assert mensajes[0][0] == "3001234567"
    assert "Recordatorio" in mensajes[0][1]


def test_verificar_tomas_ignora_paciente_inexistente(monkeypatch):
    medicamento_id = ObjectId()

    medicamentos = ColeccionFalsa([
        {
            "_id": medicamento_id,
            "paciente_id": str(ObjectId()),
            "nombre": "Losartán",
            "horario": "08:00",
        }
    ])

    mensajes = []

    monkeypatch.setattr(scheduler_module, "datetime", DateTimeFalso)
    monkeypatch.setattr(scheduler_module, "medicamentos_col", medicamentos)
    monkeypatch.setattr(scheduler_module, "pacientes_col", ColeccionFalsa([]))
    monkeypatch.setattr(scheduler_module, "usuarios_col", ColeccionFalsa([]))
    monkeypatch.setattr(scheduler_module, "tomas_col", ColeccionFalsa([]))
    monkeypatch.setattr(scheduler_module, "ya_enviados", set())
    monkeypatch.setattr(
        scheduler_module,
        "enviar_sms",
        lambda telefono, mensaje: mensajes.append((telefono, mensaje)),
    )

    scheduler_module.verificar_tomas()

    assert mensajes == []


def test_iniciar_scheduler(monkeypatch):
    jobs = []

    class SchedulerFalso:
        def add_job(self, funcion, trigger, minutes):
            jobs.append({
                "funcion": funcion,
                "trigger": trigger,
                "minutes": minutes,
            })

        def start(self):
            jobs.append({"start": True})

    monkeypatch.setattr(scheduler_module, "BackgroundScheduler", SchedulerFalso)

    scheduler = scheduler_module.iniciar_scheduler()

    assert scheduler is not None
    assert jobs[0]["trigger"] == "interval"
    assert jobs[0]["minutes"] == 1
    assert jobs[1]["start"] is True