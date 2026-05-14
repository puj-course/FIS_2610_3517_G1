import time

from backend.quality_metrics import (
    calcular_completitud_datos,
    calcular_completitud_registro,
    calcular_cumplimiento_reglas_negocio,
    clasificar_latencia,
    medir_latencia_operacion,
)


def test_completitud_registro_completo():
    registro = {
        "nombres": "Valentina",
        "apellidos": "Ramirez",
        "fecha_nacimiento": "2000-01-01",
    }

    resultado = calcular_completitud_registro(
        registro,
        ["nombres", "apellidos", "fecha_nacimiento"],
    )

    assert resultado["campos_totales"] == 3
    assert resultado["campos_completos"] == 3
    assert resultado["porcentaje"] == 100.0
    assert resultado["interpretacion"] == "alto"


def test_completitud_registro_incompleto():
    registro = {
        "nombres": "Valentina",
        "apellidos": "",
        "fecha_nacimiento": None,
    }

    resultado = calcular_completitud_registro(
        registro,
        ["nombres", "apellidos", "fecha_nacimiento"],
    )

    assert resultado["campos_totales"] == 3
    assert resultado["campos_completos"] == 1
    assert resultado["porcentaje"] == 33.3
    assert resultado["interpretacion"] == "deficiente"


def test_completitud_datos_general():
    pacientes = [
        {
            "id": "pac-1",
            "nombres": "Valentina",
            "apellidos": "Ramirez",
            "fecha_nacimiento": "2000-01-01",
            "tipo_documento": "CC",
            "numero_documento": "123",
            "telefono_contacto": "3001234567",
            "diagnostico_principal": "Hipertensión",
        }
    ]

    medicamentos = [
        {
            "id": "med-1",
            "nombre": "Losartán",
            "dosis": "50 mg",
            "frecuencia": "Diaria",
            "horario": "08:00",
            "fecha_inicio": "05/01/2026",
            "paciente_id": "pac-1",
        }
    ]

    recordatorios = [
        {
            "id": "rec-1",
            "medicamento_id": "med-1",
            "paciente_id": "pac-1",
            "hora_recordatorio": "08:00",
            "fecha_inicio": "05/01/2026",
        }
    ]

    resultado = calcular_completitud_datos(
        pacientes,
        medicamentos,
        recordatorios,
    )

    assert resultado["porcentaje"] == 100.0
    assert resultado["interpretacion"] == "alto"
    assert resultado["entidades"]["pacientes"]["registros"] == 1


def test_completitud_datos_con_registros_incompletos():
    pacientes = [
        {
            "id": "pac-1",
            "nombres": "Valentina",
            "apellidos": "",
            "fecha_nacimiento": "",
            "tipo_documento": "CC",
            "numero_documento": "",
            "telefono_contacto": "",
            "diagnostico_principal": "",
        }
    ]

    resultado = calcular_completitud_datos(
        pacientes=pacientes,
        medicamentos=[],
        recordatorios=[],
    )

    assert resultado["porcentaje"] < 70
    assert resultado["interpretacion"] == "deficiente"


def test_cumplimiento_reglas_negocio_correcto():
    pacientes = [{"id": "pac-1"}]
    medicamentos = [{"id": "med-1", "paciente_id": "pac-1"}]
    recordatorios = [
        {
            "id": "rec-1",
            "paciente_id": "pac-1",
            "medicamento_id": "med-1",
        }
    ]
    tomas = [
        {
            "id": "toma-1",
            "paciente_id": "pac-1",
            "medicamento_id": "med-1",
            "recordatorio_id": "rec-1",
        }
    ]

    resultado = calcular_cumplimiento_reglas_negocio(
        pacientes,
        medicamentos,
        recordatorios,
        tomas,
    )

    assert resultado["porcentaje"] == 100.0
    assert resultado["reglas_incumplidas"] == 0
    assert resultado["interpretacion"] == "alto"


def test_cumplimiento_reglas_negocio_con_inconsistencias():
    pacientes = [{"id": "pac-1"}]
    medicamentos = [{"id": "med-1", "paciente_id": "pac-inexistente"}]
    recordatorios = [
        {
            "id": "rec-1",
            "paciente_id": "pac-1",
            "medicamento_id": "med-inexistente",
        }
    ]
    tomas = [
        {
            "id": "toma-1",
            "paciente_id": "pac-1",
            "medicamento_id": "med-1",
            "recordatorio_id": "rec-inexistente",
        }
    ]

    resultado = calcular_cumplimiento_reglas_negocio(
        pacientes,
        medicamentos,
        recordatorios,
        tomas,
    )

    assert resultado["reglas_totales"] == 6
    assert resultado["reglas_incumplidas"] == 3
    assert resultado["porcentaje"] == 50.0
    assert resultado["interpretacion"] == "deficiente"


def test_cumplimiento_reglas_negocio_sin_datos():
    resultado = calcular_cumplimiento_reglas_negocio([], [], [], [])

    assert resultado["reglas_totales"] == 0
    assert resultado["porcentaje"] == 100.0
    assert resultado["interpretacion"] == "alto"


def test_clasificar_latencia():
    assert clasificar_latencia(100) == "buena"
    assert clasificar_latencia(500) == "aceptable"
    assert clasificar_latencia(1200) == "deficiente"


def test_medir_latencia_operacion_exitosa():
    resultado = medir_latencia_operacion(lambda: "ok")

    assert resultado["metrica"] == "latencia_operacion"
    assert resultado["exitoso"] is True
    assert resultado["resultado"] == "ok"
    assert resultado["latencia_ms"] >= 0


def test_medir_latencia_operacion_lenta():
    def operacion_lenta():
        time.sleep(0.01)
        return "ok"

    resultado = medir_latencia_operacion(operacion_lenta)

    assert resultado["exitoso"] is True
    assert resultado["resultado"] == "ok"
    assert resultado["latencia_ms"] >= 10


def test_medir_latencia_operacion_con_error_value_error():
    def operacion_con_error():
        raise ValueError("fallo controlado")

    resultado = medir_latencia_operacion(operacion_con_error)

    assert resultado["exitoso"] is False
    assert resultado["error"] == "fallo controlado"
    assert resultado["latencia_ms"] >= 0


def test_medir_latencia_operacion_con_error_runtime_error():
    def operacion_con_error():
        raise RuntimeError("fallo runtime")

    resultado = medir_latencia_operacion(operacion_con_error)

    assert resultado["exitoso"] is False
    assert resultado["error"] == "fallo runtime"
