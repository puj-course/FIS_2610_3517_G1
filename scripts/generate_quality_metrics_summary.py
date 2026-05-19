import json
from pathlib import Path


REPORT_DIR = Path("reports/quality")
VALID_JSON = REPORT_DIR / "quality_metrics_valid_result.json"
INVALID_JSON = REPORT_DIR / "quality_metrics_invalid_result.json"
OUTPUT_MD = REPORT_DIR / "quality_metrics_pr_summary.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo requerido: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def get_reporte(data: dict) -> dict:
    if "resumen_metricas" in data:
        return data

    if "resultado" in data and isinstance(data["resultado"], dict):
        return data["resultado"]

    if "reporte" in data and isinstance(data["reporte"], dict):
        return data["reporte"]

    return data


def get_estado(data: dict) -> str:
    reporte = get_reporte(data)

    if "estado_general" in reporte:
        return str(reporte["estado_general"])

    if "quality_gate_aprobado" in reporte:
        return "Aprobado" if reporte["quality_gate_aprobado"] else "Requiere mejora"

    return "No disponible"


def get_resumen(data: dict) -> dict:
    reporte = get_reporte(data)
    return reporte.get("resumen_metricas", {})


def get_metrica(resumen: dict, nombre: str) -> dict:
    return resumen.get(nombre, {})


def porcentaje(metrica: dict) -> str:
    valor = metrica.get("porcentaje", metrica.get("valor", "N/D"))

    if isinstance(valor, (int, float)):
        return f"{valor:.1f}%"

    return str(valor)


def nivel(metrica: dict) -> str:
    return str(metrica.get("nivel", metrica.get("clasificacion", "N/D")))


def detalle_completitud(metrica: dict) -> str:
    completos = metrica.get("campos_completos", "N/D")
    totales = metrica.get("campos_totales", "N/D")
    return f"{completos}/{totales} campos completos"


def detalle_reglas(metrica: dict) -> str:
    cumplidas = metrica.get("reglas_cumplidas", "N/D")
    totales = metrica.get("reglas_totales", "N/D")
    return f"{cumplidas}/{totales} reglas cumplidas"


def detalle_rendimiento(metrica: dict) -> str:
    latencia = metrica.get("latencia_ms", metrica.get("tiempo_ms", "N/D"))
    objetivo = metrica.get("objetivo_ms", "N/D")
    return f"latencia {latencia} ms / objetivo {objetivo} ms"


def main() -> None:
    valid = load_json(VALID_JSON)
    invalid = load_json(INVALID_JSON)

    valid_estado = get_estado(valid)
    invalid_estado = get_estado(invalid)

    valid_resumen = get_resumen(valid)
    invalid_resumen = get_resumen(invalid)

    valid_completitud = get_metrica(valid_resumen, "completitud_datos")
    valid_reglas = get_metrica(valid_resumen, "cumplimiento_reglas_negocio")
    valid_rendimiento = get_metrica(valid_resumen, "rendimiento_latencia")

    invalid_completitud = get_metrica(invalid_resumen, "completitud_datos")
    invalid_reglas = get_metrica(invalid_resumen, "cumplimiento_reglas_negocio")
    invalid_rendimiento = get_metrica(invalid_resumen, "rendimiento_latencia")

    markdown = f"""# ✅ Quality Metrics - MedTrack

Este resumen fue generado automáticamente por GitHub Actions.

## Resultado general

| Escenario | Resultado esperado | Resultado obtenido |
|---|---|---|
| Escenario válido | Aprobado | {valid_estado} |
| Escenario inválido | Requiere mejora | {invalid_estado} |

## Métricas por porcentaje

| Métrica | Escenario válido | Nivel | Detalle válido | Escenario inválido | Nivel | Detalle inválido |
|---|---:|---|---|---:|---|---|
| Completitud de datos | {porcentaje(valid_completitud)} | {nivel(valid_completitud)} | {detalle_completitud(valid_completitud)} | {porcentaje(invalid_completitud)} | {nivel(invalid_completitud)} | {detalle_completitud(invalid_completitud)} |
| Cumplimiento de reglas de negocio | {porcentaje(valid_reglas)} | {nivel(valid_reglas)} | {detalle_reglas(valid_reglas)} | {porcentaje(invalid_reglas)} | {nivel(invalid_reglas)} | {detalle_reglas(invalid_reglas)} |
| Rendimiento / latencia | {porcentaje(valid_rendimiento)} | {nivel(valid_rendimiento)} | {detalle_rendimiento(valid_rendimiento)} | {porcentaje(invalid_rendimiento)} | {nivel(invalid_rendimiento)} | {detalle_rendimiento(invalid_rendimiento)} |

## Interpretación

- **Completitud de datos:** mide campos obligatorios completos sobre campos obligatorios totales.
- **Cumplimiento de reglas de negocio:** mide coherencia entre paciente, medicamento, recordatorio y toma.
- **Rendimiento / latencia:** mide el porcentaje de cumplimiento del objetivo de tiempo del backend.
- El escenario inválido debe fallar para demostrar que las métricas detectan datos incoherentes.

## Evidencia de integración

- Ruta frontend: `/metricas-calidad`
- Endpoint con datos reales: `GET /metricas-calidad/resumen`
- Endpoint con escenarios editables: `POST /metricas-calidad/evaluar`
- Artifacts generados: `reports/quality/`
"""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")

    print(markdown)


if __name__ == "__main__":
    main()