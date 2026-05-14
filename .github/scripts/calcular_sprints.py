# .github/scripts/calcular_sprints.py
import json
import os
from datetime import datetime, timezone

repo        = os.environ["REPO"]
NUM_SPRINTS = 14

with open("/tmp/issues.json") as f:
    issues = json.load(f)

# Filtramos PRs (GitHub los mezcla con issues)
issues = [i for i in issues if "pull_request" not in i]

# Contamos HU cerradas por sprint según su etiqueta
conteo       = {n: 0 for n in range(1, NUM_SPRINTS + 1)}
sin_etiqueta = 0

for issue in issues:
    sprint_encontrado = None
    for label in issue.get("labels", []):
        if label["name"].startswith("sprint-"):
            try:
                sprint_encontrado = int(label["name"].replace("sprint-", ""))
            except ValueError:
                pass
    if sprint_encontrado and sprint_encontrado in conteo:
        conteo[sprint_encontrado] += 1
    else:
        sin_etiqueta += 1

total_cerradas      = sum(conteo.values())
sprints_con_hu      = [n for n in conteo if conteo[n] > 0]
num_sprints_activos = len(sprints_con_hu)
promedio            = round(total_cerradas / num_sprints_activos, 1) if num_sprints_activos else 0
fecha               = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

# Construimos el reporte línea por línea para evitar problemas con | en YAML
lineas = [
    f"# HU Cerradas por Sprint",
    f"> Generado el {fecha}",
    "",
    "| Sprint | HU Cerradas |",
    "|---|---|",
]

for n in range(1, NUM_SPRINTS + 1):
    lineas.append(f"| Sprint {n} | {conteo[n]} |")

lineas += [
    f"| **Total** | **{total_cerradas}** |",
    f"| **Promedio por sprint** | **{promedio}** |",
    "",
]

if sin_etiqueta:
    lineas.append(f"> {sin_etiqueta} HU cerradas no tienen etiqueta de sprint y no fueron contadas.")

lineas.append(f"\n---\n*[Ver workflow](https://github.com/{repo}/actions)*")

reporte = "\n".join(lineas)

with open("/tmp/reporte.md", "w") as f:
    f.write(reporte)

print(reporte)