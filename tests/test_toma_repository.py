########################################################################################
# test_toma_repository.py
########################################################################################

from unittest.mock import MagicMock
from bson import ObjectId

from backend import toma_repository as repo_module
from backend.toma_repository import TomaRepository


PACIENTE_ID = "69feaac76a52afc46ed40c52"
MEDICAMENTO_ID = "69feb355322be070cd1c97ce"
TOMA_ID = ObjectId("69feb500322be070cd1c97d0")


def test_registrar_toma(monkeypatch):
    tomas_col = MagicMock()

    resultado_insert = MagicMock()
    resultado_insert.inserted_id = TOMA_ID

    tomas_col.insert_one.return_value = resultado_insert

    monkeypatch.setattr(repo_module, "tomas_col", tomas_col)

    repo = TomaRepository()

    toma_id = repo.registrar_toma(
        medicamento_id=MEDICAMENTO_ID,
        paciente_id=PACIENTE_ID,
        fecha="2026-04-13",
        hora_programada="08:00",
        hora_tomada="08:04",
        estado="tomada",
        observaciones="Nueva toma",
    )

    assert toma_id == str(TOMA_ID)

    tomas_col.insert_one.assert_called_once()

    documento = tomas_col.insert_one.call_args.args[0]

    assert documento["medicamento_id"] == MEDICAMENTO_ID
    assert documento["paciente_id"] == PACIENTE_ID
    assert documento["fecha"] == "2026-04-13"
    assert documento["hora_programada"] == "08:00"
    assert documento["hora_tomada"] == "08:04"
    assert documento["estado"] == "tomada"
    assert documento["observaciones"] == "Nueva toma"


def test_valores_default(monkeypatch):
    tomas_col = MagicMock()

    resultado_insert = MagicMock()
    resultado_insert.inserted_id = TOMA_ID

    tomas_col.insert_one.return_value = resultado_insert

    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [
        {
            "_id": TOMA_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "paciente_id": PACIENTE_ID,
            "fecha": "2026-04-14",
            "hora_programada": "09:00",
            "hora_tomada": None,
            "estado": "pendiente",
            "observaciones": None,
        }
    ]

    tomas_col.find.return_value = cursor_mock

    monkeypatch.setattr(repo_module, "tomas_col", tomas_col)

    repo = TomaRepository()

    toma_id = repo.registrar_toma(
        medicamento_id=MEDICAMENTO_ID,
        paciente_id=PACIENTE_ID,
        fecha="2026-04-14",
        hora_programada="09:00",
    )

    tomas = repo.obtener_tomas_del_dia(
        paciente_id=PACIENTE_ID,
        fecha="2026-04-14",
    )

    assert toma_id == str(TOMA_ID)
    assert len(tomas) == 1
    assert tomas[0]["estado"] == "pendiente"
    assert tomas[0]["hora_tomada"] is None
    assert tomas[0]["observaciones"] is None


def test_tomas_del_dia(monkeypatch):
    tomas_col = MagicMock()

    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [
        {
            "_id": TOMA_ID,
            "medicamento_id": MEDICAMENTO_ID,
            "paciente_id": PACIENTE_ID,
            "fecha": "2026-04-12",
            "hora_programada": "08:00",
            "hora_tomada": "08:05",
            "estado": "tomada",
            "observaciones": "Toma inicial",
        }
    ]

    tomas_col.find.return_value = cursor_mock

    monkeypatch.setattr(repo_module, "tomas_col", tomas_col)

    repo = TomaRepository()

    tomas = repo.obtener_tomas_del_dia(
        paciente_id=PACIENTE_ID,
        fecha="2026-04-12",
    )

    assert len(tomas) == 1
    assert tomas[0]["id"] == str(TOMA_ID)
    assert tomas[0]["medicamento_id"] == MEDICAMENTO_ID
    assert tomas[0]["paciente_id"] == PACIENTE_ID
    assert tomas[0]["estado"] == "tomada"


def test_tomas_vacio(monkeypatch):
    tomas_col = MagicMock()

    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = []

    tomas_col.find.return_value = cursor_mock

    monkeypatch.setattr(repo_module, "tomas_col", tomas_col)

    repo = TomaRepository()

    tomas = repo.obtener_tomas_del_dia(
        paciente_id="paciente-sin-tomas",
        fecha="2026-04-12",
    )

    assert tomas == []