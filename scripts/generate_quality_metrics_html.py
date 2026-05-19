import json
from pathlib import Path
from html import escape


REPORT_DIR = Path("reports/quality")
VALID_JSON = REPORT_DIR / "quality_metrics_valid_result.json"
INVALID_JSON = REPORT_DIR / "quality_metrics_invalid_result.json"
SUMMARY_MD = REPORT_DIR / "quality_metrics_summary.md"
OUTPUT_HTML = REPORT_DIR / "quality_metrics_report.html"
OUTPUT_INDEX = REPORT_DIR / "index.html"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def buscar_resumen(data: dict) -> dict:
    if "resumen_metricas" in data:
        return data["resumen_metricas"]

    if "reporte" in data and isinstance(data["reporte"], dict):
        return data["reporte"].get("resumen_metricas", {})

    if "resultado" in data and isinstance(data["resultado"], dict):
        return data["resultado"].get("resumen_metricas", {})

    return {}


def buscar_estado(data: dict) -> str:
    if "estado_general" in data:
        return str(data["estado_general"])

    if "quality_gate_aprobado" in data:
        return "Aprobado" if data["quality_gate_aprobado"] else "Requiere mejora"

    if "reporte" in data and isinstance(data["reporte"], dict):
        return buscar_estado(data["reporte"])

    if "resultado" in data and isinstance(data["resultado"], dict):
        return buscar_estado(data["resultado"])

    return "No disponible"


def buscar_metrica(resumen: dict, *nombres: str) -> dict:
    for nombre in nombres:
        if nombre in resumen and isinstance(resumen[nombre], dict):
            return resumen[nombre]
    return {}


def obtener_porcentaje(metrica: dict) -> str:
    for key in ["porcentaje", "valor", "cumplimiento_objetivo_porcentaje"]:
        if key in metrica:
            return f"{metrica[key]}%"
    return "No disponible"


def obtener_nivel(metrica: dict) -> str:
    return str(metrica.get("nivel") or metrica.get("clasificacion") or "No disponible")


def card(nombre: str, porcentaje: str, nivel: str, detalle: str = "") -> str:
    clase = "ok"
    nivel_l = nivel.lower()

    if "deficiente" in nivel_l or "requiere" in nivel_l:
        clase = "bad"
    elif "aceptable" in nivel_l:
        clase = "warn"

    return f"""
    <section class="card {clase}">
      <h3>{escape(nombre)}</h3>
      <p class="value">{escape(porcentaje)}</p>
      <p><strong>Nivel:</strong> {escape(nivel)}</p>
      <p>{escape(detalle)}</p>
    </section>
    """


def render_escenario(titulo: str, data: dict) -> str:
    resumen = buscar_resumen(data)
    estado = buscar_estado(data)

    completitud = buscar_metrica(resumen, "completitud_datos", "completitud")
    reglas = buscar_metrica(
        resumen,
        "cumplimiento_reglas_negocio",
        "reglas_negocio",
        "cumplimiento",
    )
    rendimiento = buscar_metrica(
        resumen,
        "rendimiento_latencia",
        "latencia_rendimiento",
        "rendimiento",
    )

    latencia_ms = rendimiento.get("latencia_ms", rendimiento.get("tiempo_ms", "No disponible"))
    objetivo_ms = rendimiento.get("objetivo_ms", "No disponible")

    raw_json = json.dumps(data, ensure_ascii=False, indent=2)

    return f"""
    <section class="scenario">
      <div class="scenario-header">
        <h2>{escape(titulo)}</h2>
        <span class="gate">{escape(estado)}</span>
      </div>

      <div class="cards">
        {card(
            "Completitud de datos",
            obtener_porcentaje(completitud),
            obtener_nivel(completitud),
            "Campos completos sobre campos obligatorios totales."
        )}
        {card(
            "Cumplimiento de reglas de negocio",
            obtener_porcentaje(reglas),
            obtener_nivel(reglas),
            "Reglas coherentes entre paciente, medicamento, recordatorio y toma."
        )}
        {card(
            "Rendimiento / latencia",
            obtener_porcentaje(rendimiento),
            obtener_nivel(rendimiento),
            f"Latencia real: {latencia_ms} ms. Objetivo: {objetivo_ms} ms."
        )}
      </div>

      <details>
        <summary>Ver JSON técnico del escenario</summary>
        <pre>{escape(raw_json)}</pre>
      </details>
    </section>
    """


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    valid_data = load_json(VALID_JSON)
    invalid_data = load_json(INVALID_JSON)

    summary_text = ""
    if SUMMARY_MD.exists():
        summary_text = SUMMARY_MD.read_text(encoding="utf-8")

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Reporte de métricas de calidad - MedTrack</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 32px;
      background: #0f172a;
      color: #e5e7eb;
    }}

    h1, h2, h3 {{
      color: #ffffff;
    }}

    .intro {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 24px;
    }}

    .scenario {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 24px;
    }}

    .scenario-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}

    .gate {{
      border: 1px solid #22c55e;
      color: #22c55e;
      border-radius: 999px;
      padding: 8px 14px;
      font-weight: bold;
    }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}

    .card {{
      background: #1e293b;
      border-left: 8px solid #22c55e;
      border-radius: 12px;
      padding: 18px;
    }}

    .card.warn {{
      border-left-color: #f59e0b;
    }}

    .card.bad {{
      border-left-color: #ef4444;
    }}

    .value {{
      font-size: 42px;
      font-weight: bold;
      color: #2dd4bf;
      margin: 12px 0;
    }}

    pre {{
      background: #020617;
      color: #e5e7eb;
      padding: 16px;
      border-radius: 12px;
      overflow-x: auto;
      border: 1px solid #334155;
    }}

    summary {{
      cursor: pointer;
      margin-top: 16px;
      color: #93c5fd;
    }}

    .small {{
      color: #94a3b8;
      font-size: 14px;
    }}
  </style>
</head>
<body>
  <h1>Reporte de métricas de calidad - MedTrack</h1>

  <section class="intro">
    <p>
      Este reporte HTML fue generado automáticamente desde los resultados del pipeline.
      Resume las métricas propias del sistema: completitud de datos, cumplimiento de reglas de negocio
      y rendimiento/latencia.
    </p>

    <p class="small">
      Archivos fuente:
      {escape(str(VALID_JSON))},
      {escape(str(INVALID_JSON))}
    </p>
  </section>

  {render_escenario("Escenario válido", valid_data)}
  {render_escenario("Escenario inválido", invalid_data)}

  <section class="scenario">
    <h2>Resumen del pipeline</h2>
    <pre>{escape(summary_text or "No se encontró quality_metrics_summary.md")}</pre>
  </section>
</body>
</html>
"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    OUTPUT_INDEX.write_text(html, encoding="utf-8")

    print(f"Reporte HTML generado en: {OUTPUT_HTML}")
    print(f"Index HTML generado en: {OUTPUT_INDEX}")


if __name__ == "__main__":
    main()
