from __future__ import annotations

from time import perf_counter
from typing import Any, Callable


UMBRAL_ALTO = 90.0
UMBRAL_ACEPTABLE = 70.0

LATENCIA_BUENA_MS = 300.0
LATENCIA_ACEPTABLE_MS = 1000.0

CAMPOS_PACIENTE = [
    "nombres",
    "apellidos",
    "fecha_nacimiento",
    "tipo_documento",
    "numero_documento",
    "telefono_contacto",
    "diagnostico_principal",
]

CAMPOS_MEDICAMENTO = [
    "nombre",
    "dosis",
    "frecuencia",
    "horario",
    "fecha_inicio",
    "paciente_id",
]

CAMPOS_RECORDATORIO = [
    "medicamento_id",
    "paciente_id",
    "hora_recordatorio",
    "fecha_inicio",
]


def _obtener_id(documento: dict[str, Any]) -> str:
    return str(documento.get("_id") or documento.get("id") or "")


def _tiene_valor(valor: Any) -> bool:
    if valor is None:
        return False

    if isinstance(valor, str):
        return bool(valor.strip())

    if isinstance(valor, list):
        return len(valor) > 0

    return True


def interpretar_porcentaje(porcentaje: float) -> str:
    if porcentaje >= UMBRAL_ALTO:
        return "alto"

    if porcentaje >= UMBRAL_ACEPTABLE:
        return "aceptable"

    return "deficiente"


def calcular_completitud_registro(
    registro: dict[str, Any],
    campos_requeridos: list[str],
) -> dict[str, Any]:
    total_campos = len(campos_requeridos)

    if total_campos == 0:
        return {
            "campos_totales": 0,
            "campos_completos": 0,
            "porcentaje": 100.0,
            "interpretacion": "alto",
        }

    campos_completos = sum(
        1
        for campo in campos_requeridos
        if _tiene_valor(registro.get(campo))
    )

    porcentaje = round((campos_completos / total_campos) * 100, 1)

    return {
        "campos_totales": total_campos,
        "campos_completos": campos_completos,
        "porcentaje": porcentaje,
        "interpretacion": interpretar_porcentaje(porcentaje),
    }


def _calcular_completitud_coleccion(
    registros: list[dict[str, Any]],
    campos_requeridos: list[str],
) -> dict[str, Any]:
    total_campos = len(registros) * len(campos_requeridos)

    if total_campos == 0:
        return {
            "registros": len(registros),
            "campos_totales": 0,
            "campos_completos": 0,
            "porcentaje": 0.0,
            "interpretacion": "deficiente",
        }

    campos_completos = sum(
        calcular_completitud_registro(
            registro,
            campos_requeridos,
        )["campos_completos"]
        for registro in registros
    )

    porcentaje = round((campos_completos / total_campos) * 100, 1)

    return {
        "registros": len(registros),
        "campos_totales": total_campos,
        "campos_completos": campos_completos,
        "porcentaje": porcentaje,
        "interpretacion": interpretar_porcentaje(porcentaje),
    }


def calcular_completitud_datos(
    pacientes: list[dict[str, Any]],
    medicamentos: list[dict[str, Any]],
    recordatorios: list[dict[str, Any]],
) -> dict[str, Any]:
    entidades = {
        "pacientes": _calcular_completitud_coleccion(
            pacientes,
            CAMPOS_PACIENTE,
        ),
        "medicamentos": _calcular_completitud_coleccion(
            medicamentos,
            CAMPOS_MEDICAMENTO,
        ),
        "recordatorios": _calcular_completitud_coleccion(
            recordatorios,
            CAMPOS_RECORDATORIO,
        ),
    }

    campos_totales = sum(
        entidad["campos_totales"]
        for entidad in entidades.values()
    )
    campos_completos = sum(
        entidad["campos_completos"]
        for entidad in entidades.values()
    )

    porcentaje = (
        round((campos_completos / campos_totales) * 100, 1)
        if campos_totales > 0
        else 0.0
    )

    return {
        "metrica": "completitud_datos",
        "campos_totales": campos_totales,
        "campos_completos": campos_completos,
        "porcentaje": porcentaje,
        "interpretacion": interpretar_porcentaje(porcentaje),
        "entidades": entidades,
    }


def _registrar_resultado_regla(
    resultados: list[dict[str, Any]],
    regla: str,
    cumple: bool,
    referencia: str,
) -> None:
    resultados.append({
        "regla": regla,
        "cumple": cumple,
        "referencia": referencia,
    })


def calcular_cumplimiento_reglas_negocio(
    pacientes: list[dict[str, Any]],
    medicamentos: list[dict[str, Any]],
    recordatorios: list[dict[str, Any]],
    tomas: list[dict[str, Any]],
) -> dict[str, Any]:
    pacientes_ids = {_obtener_id(paciente) for paciente in pacientes}
    medicamentos_ids = {_obtener_id(medicamento) for medicamento in medicamentos}
    recordatorios_ids = {_obtener_id(recordatorio) for recordatorio in recordatorios}

    resultados = []

    for medicamento in medicamentos:
        paciente_id = str(medicamento.get("paciente_id", ""))
        _registrar_resultado_regla(
            resultados,
            "Medicamento asociado a paciente existente",
            paciente_id in pacientes_ids,
            _obtener_id(medicamento),
        )

    for recordatorio in recordatorios:
        medicamento_id = str(recordatorio.get("medicamento_id", ""))
        paciente_id = str(recordatorio.get("paciente_id", ""))

        _registrar_resultado_regla(
            resultados,
            "Recordatorio asociado a medicamento existente",
            medicamento_id in medicamentos_ids,
            _obtener_id(recordatorio),
        )

        _registrar_resultado_regla(
            resultados,
            "Recordatorio asociado a paciente existente",
            paciente_id in pacientes_ids,
            _obtener_id(recordatorio),
        )

    for toma in tomas:
        paciente_id = str(toma.get("paciente_id", ""))
        medicamento_id = str(toma.get("medicamento_id", ""))
        recordatorio_id = str(toma.get("recordatorio_id", ""))

        _registrar_resultado_regla(
            resultados,
            "Toma asociada a paciente existente",
            paciente_id in pacientes_ids,
            _obtener_id(toma),
        )

        _registrar_resultado_regla(
            resultados,
            "Toma asociada a medicamento existente",
            medicamento_id in medicamentos_ids,
            _obtener_id(toma),
        )

        _registrar_resultado_regla(
            resultados,
            "Toma asociada a recordatorio existente",
            recordatorio_id in recordatorios_ids,
            _obtener_id(toma),
        )

    total_reglas = len(resultados)
    reglas_cumplidas = sum(
        1
        for resultado in resultados
        if resultado["cumple"]
    )

    porcentaje = (
        round((reglas_cumplidas / total_reglas) * 100, 1)
        if total_reglas > 0
        else 100.0
    )

    return {
        "metrica": "cumplimiento_reglas_negocio",
        "reglas_totales": total_reglas,
        "reglas_cumplidas": reglas_cumplidas,
        "reglas_incumplidas": total_reglas - reglas_cumplidas,
        "porcentaje": porcentaje,
        "interpretacion": interpretar_porcentaje(porcentaje),
        "detalle": resultados,
    }


def clasificar_latencia(latencia_ms: float) -> str:
    if latencia_ms < LATENCIA_BUENA_MS:
        return "buena"

    if latencia_ms <= LATENCIA_ACEPTABLE_MS:
        return "aceptable"

    return "deficiente"


def _calcular_latencia_ms(inicio: float) -> float:
    return round((perf_counter() - inicio) * 1000, 2)


def _construir_resultado_latencia_error(
    inicio: float,
    exc: Exception,
) -> dict[str, Any]:
    latencia_ms = _calcular_latencia_ms(inicio)

    return {
        "metrica": "latencia_operacion",
        "exitoso": False,
        "latencia_ms": latencia_ms,
        "interpretacion": clasificar_latencia(latencia_ms),
        "error": str(exc),
    }


def medir_latencia_operacion(
    operacion: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    inicio = perf_counter()

    try:
        resultado = operacion(*args, **kwargs)
    except (ValueError, RuntimeError, LookupError) as exc:
        return _construir_resultado_latencia_error(inicio, exc)

    latencia_ms = _calcular_latencia_ms(inicio)

    return {
        "metrica": "latencia_operacion",
        "exitoso": True,
        "latencia_ms": latencia_ms,
        "interpretacion": clasificar_latencia(latencia_ms),
        "resultado": resultado,
    }