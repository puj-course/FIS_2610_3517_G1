from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.quality_metrics import construir_reporte_metricas  # noqa: E402


DATA_DIR = ROOT / "data" / "quality"
REPORTS_DIR = ROOT / "reports" / "quality"

ESCENARIOS = {
    "valid": DATA_DIR / "quality_metrics_valid.json",
    "invalid": DATA_DIR / "quality_metrics_invalid.json",
}


def _leer_json(ruta: Path) -> dict[str, Any]:
    return json.loads(ruta.read_text(encoding="utf-8"))


def _escribir_json(ruta: Path, contenido: dict[str, Any]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(contenido, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _calcular(payload: dict[str, Any]) -> dict[str, Any]:
    return construir_reporte_metricas(
        pacientes=payload.get("pacientes", []),
        medicamentos=payload.get("medicamentos", []),
        recordatorios=payload.get("recordatorios", []),
        tomas=payload.get("tomas", []),
        objetivo_ms=float(payload.get("objetivo_ms", 300)),
        incluir_detalle=True,
    )


def _validar_porcentajes(reporte: dict[str, Any], nombre: str) -> None:
    for clave, metrica in reporte.get("resumen_metricas", {}).items():
        if "porcentaje" not in metrica:
            raise SystemExit(f"El escenario {nombre} no trae porcentaje en {clave}.")


def _linea_metricas(reporte: dict[str, Any]) -> list[str]:
    metricas = reporte["resumen_metricas"]
    return [
        (
            "Completitud de datos: "
            f"{metricas['completitud_datos']['porcentaje']}%."
        ),
        (
            "Cumplimiento de reglas de negocio: "
            f"{metricas['cumplimiento_reglas_negocio']['porcentaje']}%."
        ),
        (
            "Rendimiento / latencia: "
            f"{metricas['rendimiento_latencia']['porcentaje']}% "
            "de cumplimiento del objetivo."
        ),
    ]


def _crear_resumen_markdown(resultados: dict[str, dict[str, Any]]) -> str:
    valido = resultados["valid"]
    invalido = resultados["invalid"]
    metricas_validas = valido["resumen_metricas"]
    metricas_invalidas = invalido["resumen_metricas"]

    return "\n".join([
        "## Quality Metrics",
        "",
        f"- Completitud de datos: {metricas_validas['completitud_datos']['porcentaje']}% en escenario valido.",
        (
            "- Cumplimiento de reglas de negocio: "
            f"{metricas_validas['cumplimiento_reglas_negocio']['porcentaje']}% en escenario valido; "
            f"{metricas_invalidas['cumplimiento_reglas_negocio']['porcentaje']}% en escenario invalido."
        ),
        (
            "- Rendimiento: "
            f"{metricas_validas['rendimiento_latencia']['porcentaje']}% "
            "de cumplimiento del objetivo."
        ),
        f"- Escenario valido: {'aprobado' if valido['quality_gate_aprobado'] else 'fallo'}.",
        (
            "- Escenario invalido: "
            f"{'fallo como se esperaba' if not invalido['quality_gate_aprobado'] else 'aprobo inesperadamente'}."
        ),
        "- Ruta frontend: /metricas-calidad.",
        "- Endpoints: GET /metricas-calidad/resumen y POST /metricas-calidad/evaluar.",
        "",
    ])


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    resultados: dict[str, dict[str, Any]] = {}

    for nombre, ruta in ESCENARIOS.items():
        payload = _leer_json(ruta)
        reporte = _calcular(payload)
        _validar_porcentajes(reporte, nombre)
        resultados[nombre] = reporte

        salida = REPORTS_DIR / f"quality_metrics_{nombre}_result.json"
        _escribir_json(salida, reporte)

        print(f"Escenario {nombre}:")
        for linea in _linea_metricas(reporte):
            print(f"- {linea}")

    if not resultados["valid"]["quality_gate_aprobado"]:
        raise SystemExit("El escenario valido no aprobo el quality gate.")

    if resultados["invalid"]["quality_gate_aprobado"]:
        raise SystemExit("El escenario invalido aprobo, pero debia fallar.")

    reglas_invalidas = resultados["invalid"]["resumen_metricas"]["cumplimiento_reglas_negocio"]
    if reglas_invalidas["porcentaje"] >= 70:
        raise SystemExit("El escenario invalido no dejo las reglas de negocio en estado deficiente.")

    resumen = _crear_resumen_markdown(resultados)
    (REPORTS_DIR / "quality_metrics_summary.md").write_text(
        resumen,
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
