from __future__ import annotations

from time import perf_counter
from typing import Any, Callable


UMBRAL_BUENO = 90.0
UMBRAL_ACEPTABLE = 70.0
OBJETIVO_LATENCIA_MS = 300.0

QUE_MIDE_COMPLETITUD = "Porcentaje de campos obligatorios completos."
CAMBIO_COMPLETITUD = (
    "Baja cuando faltan campos requeridos en pacientes, medicamentos o "
    "recordatorios."
)

QUE_MIDE_REGLAS = "Porcentaje de reglas de negocio cumplidas."
CAMBIO_REGLAS = (
    "Baja cuando los IDs no existen o no son coherentes entre paciente, "
    "medicamento, recordatorio y toma."
)

QUE_MIDE_RENDIMIENTO = "Porcentaje de cumplimiento del objetivo de rendimiento."
CAMBIO_RENDIMIENTO = "Baja si el calculo tarda mas que el objetivo definido."

CAMPOS_REQUERIDOS = {
    "pacientes": [
        ("paciente_id", ["paciente_id", "id", "_id"]),
        ("nombre_o_identificador", ["nombre", "nombres", "identificador", "numero_documento"]),
    ],
    "medicamentos": [
        ("medicamento_id", ["medicamento_id", "id", "_id"]),
        ("nombre", ["nombre", "nombre_medicamento", "medicamento", "medicamento_nombre"]),
        ("dosis", ["dosis", "dosis_cantidad"]),
        ("paciente_id", ["paciente_id"]),
    ],
    "recordatorios": [
        ("recordatorio_id", ["recordatorio_id", "id", "_id"]),
        ("paciente_id", ["paciente_id"]),
        ("medicamento_id", ["medicamento_id"]),
        ("hora_programada", ["hora_programada", "hora_recordatorio", "hora", "horario"]),
        ("frecuencia", ["frecuencia", "periodicidad"]),
    ],
}


def _tiene_valor(valor: Any) -> bool:
    if valor is None:
        return False

    if isinstance(valor, str):
        return bool(valor.strip())

    if isinstance(valor, (list, tuple, set, dict)):
        return len(valor) > 0

    return True


def _normalizar_valor(valor: Any) -> str:
    if valor is None:
        return ""

    return str(valor).strip()


def _obtener_primer_valor(documento: dict[str, Any], aliases: list[str]) -> Any:
    for alias in aliases:
        if alias in documento and _tiene_valor(documento.get(alias)):
            return documento.get(alias)

    return None


def _obtener_id(documento: dict[str, Any], tipo: str = "generico") -> str:
    aliases_por_tipo = {
        "paciente": ["paciente_id", "id", "_id"],
        "medicamento": ["medicamento_id", "id", "_id"],
        "recordatorio": ["recordatorio_id", "id", "_id"],
        "toma": ["toma_id", "id", "_id"],
        "generico": ["id", "_id"],
    }
    return _normalizar_valor(
        _obtener_primer_valor(documento, aliases_por_tipo.get(tipo, aliases_por_tipo["generico"]))
    )


def _obtener_referencia(documento: dict[str, Any], tipo: str) -> str:
    return _obtener_id(documento, tipo) or "sin-id"


def _obtener_relacion(documento: dict[str, Any], campo: str) -> str:
    return _normalizar_valor(documento.get(campo))


def _redondear_porcentaje(valor: float) -> float:
    return round(max(0.0, min(100.0, valor)), 1)


def interpretar_porcentaje(porcentaje: float) -> str:
    if porcentaje >= UMBRAL_BUENO:
        return "Bueno"

    if porcentaje >= UMBRAL_ACEPTABLE:
        return "Aceptable"

    return "Deficiente"


def _lectura(porcentaje: float) -> str:
    return f"{porcentaje:.1f}% - {interpretar_porcentaje(porcentaje)}"


def _cumple_quality_gate(metrica: dict[str, Any]) -> bool:
    return float(metrica.get("porcentaje", 0.0)) >= UMBRAL_ACEPTABLE


def _calcular_porcentaje(parte: int, total: int) -> float:
    if total <= 0:
        return 0.0

    return _redondear_porcentaje((parte / total) * 100)


def calcular_completitud_registro(
    registro: dict[str, Any],
    campos_requeridos: list[tuple[str, list[str]]],
) -> dict[str, Any]:
    campos = []

    for nombre_campo, aliases in campos_requeridos:
        completo = _tiene_valor(_obtener_primer_valor(registro, aliases))
        campos.append({
            "campo": nombre_campo,
            "cumple": completo,
        })

    total_campos = len(campos)
    campos_completos = sum(1 for campo in campos if campo["cumple"])
    porcentaje = _calcular_porcentaje(campos_completos, total_campos)

    return {
        "campos_totales": total_campos,
        "campos_completos": campos_completos,
        "campos_faltantes": [
            campo["campo"]
            for campo in campos
            if not campo["cumple"]
        ],
        "porcentaje": porcentaje,
        "nivel": interpretar_porcentaje(porcentaje),
        "lectura": _lectura(porcentaje),
    }


def _calcular_completitud_coleccion(
    nombre_entidad: str,
    registros: list[dict[str, Any]],
) -> dict[str, Any]:
    campos_requeridos = CAMPOS_REQUERIDOS[nombre_entidad]
    detalle = []
    campos_totales = 0
    campos_completos = 0

    for registro in registros:
        resultado = calcular_completitud_registro(registro, campos_requeridos)
        campos_totales += resultado["campos_totales"]
        campos_completos += resultado["campos_completos"]
        detalle.append({
            "id": _obtener_referencia(registro, nombre_entidad[:-1]),
            "campos_faltantes": resultado["campos_faltantes"],
            "porcentaje": resultado["porcentaje"],
            "nivel": resultado["nivel"],
        })

    porcentaje = _calcular_porcentaje(campos_completos, campos_totales)

    return {
        "registros": len(registros),
        "campos_totales": campos_totales,
        "campos_completos": campos_completos,
        "campos_incompletos": campos_totales - campos_completos,
        "porcentaje": porcentaje,
        "nivel": interpretar_porcentaje(porcentaje),
        "lectura": _lectura(porcentaje),
        "detalle": detalle,
    }


def calcular_completitud_datos(
    pacientes: list[dict[str, Any]],
    medicamentos: list[dict[str, Any]],
    recordatorios: list[dict[str, Any]],
) -> dict[str, Any]:
    entidades = {
        "pacientes": _calcular_completitud_coleccion("pacientes", pacientes),
        "medicamentos": _calcular_completitud_coleccion("medicamentos", medicamentos),
        "recordatorios": _calcular_completitud_coleccion("recordatorios", recordatorios),
    }

    campos_totales = sum(entidad["campos_totales"] for entidad in entidades.values())
    campos_completos = sum(entidad["campos_completos"] for entidad in entidades.values())
    porcentaje = _calcular_porcentaje(campos_completos, campos_totales)

    return {
        "metrica": "completitud_datos",
        "porcentaje": porcentaje,
        "nivel": interpretar_porcentaje(porcentaje),
        "lectura": _lectura(porcentaje),
        "que_mide": QUE_MIDE_COMPLETITUD,
        "que_hace_que_cambie": CAMBIO_COMPLETITUD,
        "campos_totales": campos_totales,
        "campos_completos": campos_completos,
        "campos_incompletos": campos_totales - campos_completos,
        "entidades": entidades,
    }


def _indexar_por_id(registros: list[dict[str, Any]], tipo: str) -> dict[str, dict[str, Any]]:
    return {
        _obtener_id(registro, tipo): registro
        for registro in registros
        if _obtener_id(registro, tipo)
    }


def _registrar_regla(
    resultados: list[dict[str, Any]],
    entidad: str,
    referencia: str,
    regla: str,
    cumple: bool,
    esperado: str,
    obtenido: str,
) -> None:
    resultados.append({
        "entidad": entidad,
        "referencia": referencia,
        "regla": regla,
        "cumple": bool(cumple),
        "esperado": esperado,
        "obtenido": obtenido,
    })


def _paciente_de_medicamento(medicamento: dict[str, Any] | None) -> str:
    if not medicamento:
        return ""

    return _obtener_relacion(medicamento, "paciente_id")


def _evaluar_medicamentos(
    resultados: list[dict[str, Any]],
    medicamentos: list[dict[str, Any]],
    pacientes_por_id: dict[str, dict[str, Any]],
) -> None:
    for medicamento in medicamentos:
        medicamento_id = _obtener_referencia(medicamento, "medicamento")
        paciente_id = _obtener_relacion(medicamento, "paciente_id")

        _registrar_regla(
            resultados,
            "medicamento",
            medicamento_id,
            "Medicamento asociado a paciente existente",
            paciente_id in pacientes_por_id,
            "paciente_id registrado en pacientes",
            paciente_id or "vacio",
        )


def _evaluar_recordatorios(
    resultados: list[dict[str, Any]],
    recordatorios: list[dict[str, Any]],
    pacientes_por_id: dict[str, dict[str, Any]],
    medicamentos_por_id: dict[str, dict[str, Any]],
) -> None:
    for recordatorio in recordatorios:
        recordatorio_id = _obtener_referencia(recordatorio, "recordatorio")
        paciente_id = _obtener_relacion(recordatorio, "paciente_id")
        medicamento_id = _obtener_relacion(recordatorio, "medicamento_id")
        medicamento = medicamentos_por_id.get(medicamento_id)
        paciente_medicamento_id = _paciente_de_medicamento(medicamento)

        _registrar_regla(
            resultados,
            "recordatorio",
            recordatorio_id,
            "Recordatorio asociado a medicamento existente",
            medicamento_id in medicamentos_por_id,
            "medicamento_id registrado en medicamentos",
            medicamento_id or "vacio",
        )
        _registrar_regla(
            resultados,
            "recordatorio",
            recordatorio_id,
            "Recordatorio asociado a paciente existente",
            paciente_id in pacientes_por_id,
            "paciente_id registrado en pacientes",
            paciente_id or "vacio",
        )
        _registrar_regla(
            resultados,
            "recordatorio",
            recordatorio_id,
            "Paciente del recordatorio coincide con paciente del medicamento",
            bool(medicamento) and paciente_id == paciente_medicamento_id,
            paciente_medicamento_id or "paciente del medicamento existente",
            paciente_id or "vacio",
        )


def _evaluar_tomas(
    resultados: list[dict[str, Any]],
    tomas: list[dict[str, Any]],
    pacientes_por_id: dict[str, dict[str, Any]],
    medicamentos_por_id: dict[str, dict[str, Any]],
    recordatorios_por_id: dict[str, dict[str, Any]],
) -> None:
    for toma in tomas:
        toma_id = _obtener_referencia(toma, "toma")
        paciente_id = _obtener_relacion(toma, "paciente_id")
        medicamento_id = _obtener_relacion(toma, "medicamento_id")
        recordatorio_id = _obtener_relacion(toma, "recordatorio_id")
        medicamento = medicamentos_por_id.get(medicamento_id)
        recordatorio = recordatorios_por_id.get(recordatorio_id)
        paciente_medicamento_id = _paciente_de_medicamento(medicamento)

        _registrar_regla(
            resultados,
            "toma",
            toma_id,
            "Toma asociada a paciente existente",
            paciente_id in pacientes_por_id,
            "paciente_id registrado en pacientes",
            paciente_id or "vacio",
        )
        _registrar_regla(
            resultados,
            "toma",
            toma_id,
            "Toma asociada a medicamento existente",
            medicamento_id in medicamentos_por_id,
            "medicamento_id registrado en medicamentos",
            medicamento_id or "vacio",
        )

        if recordatorio_id:
            _registrar_regla(
                resultados,
                "toma",
                toma_id,
                "Toma asociada a recordatorio existente",
                recordatorio_id in recordatorios_por_id,
                "recordatorio_id registrado en recordatorios",
                recordatorio_id,
            )

        _registrar_regla(
            resultados,
            "toma",
            toma_id,
            "Paciente de la toma coincide con paciente del medicamento",
            bool(medicamento) and paciente_id == paciente_medicamento_id,
            paciente_medicamento_id or "paciente del medicamento existente",
            paciente_id or "vacio",
        )

        if recordatorio_id:
            recordatorio_paciente_id = _obtener_relacion(recordatorio or {}, "paciente_id")
            recordatorio_medicamento_id = _obtener_relacion(recordatorio or {}, "medicamento_id")
            coincide_recordatorio = (
                bool(recordatorio)
                and paciente_id == recordatorio_paciente_id
                and medicamento_id == recordatorio_medicamento_id
            )

            _registrar_regla(
                resultados,
                "toma",
                toma_id,
                "Toma coincide con paciente y medicamento del recordatorio",
                coincide_recordatorio,
                (
                    f"paciente_id={recordatorio_paciente_id or 'vacio'}, "
                    f"medicamento_id={recordatorio_medicamento_id or 'vacio'}"
                ),
                f"paciente_id={paciente_id or 'vacio'}, medicamento_id={medicamento_id or 'vacio'}",
            )


def calcular_cumplimiento_reglas_negocio(
    pacientes: list[dict[str, Any]],
    medicamentos: list[dict[str, Any]],
    recordatorios: list[dict[str, Any]],
    tomas: list[dict[str, Any]],
) -> dict[str, Any]:
    pacientes_por_id = _indexar_por_id(pacientes, "paciente")
    medicamentos_por_id = _indexar_por_id(medicamentos, "medicamento")
    recordatorios_por_id = _indexar_por_id(recordatorios, "recordatorio")
    resultados: list[dict[str, Any]] = []

    _evaluar_medicamentos(resultados, medicamentos, pacientes_por_id)
    _evaluar_recordatorios(
        resultados,
        recordatorios,
        pacientes_por_id,
        medicamentos_por_id,
    )
    _evaluar_tomas(
        resultados,
        tomas,
        pacientes_por_id,
        medicamentos_por_id,
        recordatorios_por_id,
    )

    total_reglas = len(resultados)
    reglas_cumplidas = sum(1 for resultado in resultados if resultado["cumple"])
    porcentaje = _calcular_porcentaje(reglas_cumplidas, total_reglas)
    reglas_fallidas = [
        resultado
        for resultado in resultados
        if not resultado["cumple"]
    ]

    return {
        "metrica": "cumplimiento_reglas_negocio",
        "porcentaje": porcentaje,
        "nivel": interpretar_porcentaje(porcentaje),
        "lectura": _lectura(porcentaje),
        "que_mide": QUE_MIDE_REGLAS,
        "que_hace_que_cambie": CAMBIO_REGLAS,
        "reglas_totales": total_reglas,
        "reglas_cumplidas": reglas_cumplidas,
        "reglas_incumplidas": total_reglas - reglas_cumplidas,
        "detalle": resultados,
        "reglas_fallidas": reglas_fallidas,
    }


def clasificar_latencia(latencia_ms: float, objetivo_ms: float = OBJETIVO_LATENCIA_MS) -> str:
    if latencia_ms <= objetivo_ms:
        return "Bueno"

    porcentaje = (objetivo_ms / latencia_ms) * 100 if latencia_ms > 0 else 100.0
    return interpretar_porcentaje(_redondear_porcentaje(porcentaje))


def calcular_rendimiento_latencia(
    funcion: Callable[..., Any],
    *args: Any,
    objetivo_ms: float = OBJETIVO_LATENCIA_MS,
    **kwargs: Any,
) -> dict[str, Any]:
    inicio = perf_counter()
    exitoso = True
    error = None
    resultado = None

    try:
        resultado = funcion(*args, **kwargs)
    except (ValueError, RuntimeError, LookupError) as exc:
        exitoso = False
        error = str(exc)

    latencia_ms = round((perf_counter() - inicio) * 1000, 2)
    porcentaje = (
        100.0
        if latencia_ms <= objetivo_ms or latencia_ms == 0
        else _redondear_porcentaje((objetivo_ms / latencia_ms) * 100)
    )

    respuesta = {
        "metrica": "rendimiento_latencia",
        "porcentaje": porcentaje,
        "nivel": interpretar_porcentaje(porcentaje),
        "lectura": _lectura(porcentaje),
        "latencia_ms": latencia_ms,
        "objetivo_ms": objetivo_ms,
        "exitoso": exitoso,
        "que_mide": QUE_MIDE_RENDIMIENTO,
        "que_hace_que_cambie": CAMBIO_RENDIMIENTO,
        "resultado": resultado,
    }

    if error:
        respuesta["error"] = error

    return respuesta


def medir_latencia_operacion(
    operacion: Callable[..., Any],
    *args: Any,
    objetivo_ms: float = OBJETIVO_LATENCIA_MS,
    **kwargs: Any,
) -> dict[str, Any]:
    return calcular_rendimiento_latencia(
        operacion,
        *args,
        objetivo_ms=objetivo_ms,
        **kwargs,
    )


def _crear_notificacion(metricas_afectadas: list[str]) -> dict[str, Any]:
    if not metricas_afectadas:
        return {
            "tipo": "APROBADO",
            "mensaje": "Todas las metricas propias cumplen el umbral minimo de calidad.",
            "metricas_afectadas": [],
        }

    return {
        "tipo": "REQUIERE_MEJORA",
        "mensaje": (
            "El quality gate fallo porque hay metricas por debajo del 70%: "
            + ", ".join(metricas_afectadas)
            + "."
        ),
        "metricas_afectadas": metricas_afectadas,
    }


def _limpiar_detalle_reporte(reporte: dict[str, Any]) -> dict[str, Any]:
    metricas = reporte["resumen_metricas"]
    metricas["completitud_datos"].pop("entidades", None)
    metricas["cumplimiento_reglas_negocio"].pop("detalle", None)
    metricas["cumplimiento_reglas_negocio"].pop("reglas_fallidas", None)
    return reporte


def construir_reporte_metricas(
    pacientes: list[dict[str, Any]],
    medicamentos: list[dict[str, Any]],
    recordatorios: list[dict[str, Any]],
    tomas: list[dict[str, Any]],
    objetivo_ms: float = OBJETIVO_LATENCIA_MS,
    incluir_detalle: bool = True,
) -> dict[str, Any]:
    def calcular_metricas_base() -> dict[str, Any]:
        return {
            "completitud_datos": calcular_completitud_datos(
                pacientes,
                medicamentos,
                recordatorios,
            ),
            "cumplimiento_reglas_negocio": calcular_cumplimiento_reglas_negocio(
                pacientes,
                medicamentos,
                recordatorios,
                tomas,
            ),
        }

    rendimiento = calcular_rendimiento_latencia(
        calcular_metricas_base,
        objetivo_ms=objetivo_ms,
    )
    metricas = rendimiento.pop("resultado") or {
        "completitud_datos": calcular_completitud_datos(pacientes, medicamentos, recordatorios),
        "cumplimiento_reglas_negocio": calcular_cumplimiento_reglas_negocio(
            pacientes,
            medicamentos,
            recordatorios,
            tomas,
        ),
    }
    metricas["rendimiento_latencia"] = rendimiento

    metricas_afectadas = [
        nombre
        for nombre, metrica in metricas.items()
        if not _cumple_quality_gate(metrica)
    ]
    quality_gate_aprobado = len(metricas_afectadas) == 0

    reporte = {
        "estado_general": "Aprobado" if quality_gate_aprobado else "Requiere mejora",
        "quality_gate_aprobado": quality_gate_aprobado,
        "notificacion": _crear_notificacion(metricas_afectadas),
        "resumen_metricas": metricas,
    }

    if not incluir_detalle:
        return _limpiar_detalle_reporte(reporte)

    return reporte
