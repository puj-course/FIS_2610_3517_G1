import pytest
from unittest.mock import Mock

from backend.commands.comand_base import Command
from backend.commands.invoker import CommandInvoker
from backend.commands.regisToma_command import RegisToma_command


# =========================
# COMMAND BASE
# =========================

def test_command_base_execute_lanza_not_implemented_error():
    command = Command()

    with pytest.raises(NotImplementedError, match="implementar execute"):
        command.execute()


# =========================
# INVOKER
# =========================

def test_invoker_sin_comando_lanza_value_error():
    invoker = CommandInvoker()

    with pytest.raises(ValueError, match="No se ha configurado"):
        invoker.run()


def test_invoker_ejecuta_comando_configurado():
    command = Mock()
    command.execute.return_value = {"ok": True}

    invoker = CommandInvoker()
    invoker.set_command(command)

    resultado = invoker.run()

    assert resultado == {"ok": True}
    command.execute.assert_called_once_with()


# =========================
# REGISTRAR TOMA COMMAND
# =========================

def test_registoma_command_delega_en_toma_service():
    receiver = Mock()
    receiver.registrar_toma.return_value = {
        "ok": True,
        "mensaje": "Toma registrada correctamente",
        "toma_id": 10,
    }

    command = RegisToma_command(
        receiver=receiver,
        paciente_id=1,
        medicamento_id=2,
        recordatorio_id=3,
        fecha_programada="2026-04-12 08:00:00",
        fecha_hora_toma="2026-04-12 08:03:00",
        estado="tomada",
        observaciones="Prueba automatizada",
    )

    resultado = command.execute()

    assert resultado["ok"] is True
    assert resultado["toma_id"] == 10

    receiver.registrar_toma.assert_called_once_with(
        paciente_id=1,
        medicamento_id=2,
        recordatorio_id=3,
        fecha_programada="2026-04-12 08:00:00",
        fecha_hora_toma="2026-04-12 08:03:00",
        estado="tomada",
        observaciones="Prueba automatizada",
    )
