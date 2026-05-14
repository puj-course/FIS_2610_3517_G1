# .github/scripts/calcular_sprints.py
import json
import os
from datetime import datetime, timezone

repo        = os.environ["REPO"]
NUM_SPRINTS = 14

with open("/tmp/issues.json") as f:
    issues = json.load(f)

# Filtramos PRs
issues = [i for i in issues if "pull_request" not in i]

# Contamos HU cerradas por sprint
conteo       = {n: 0 for n in range(1, NUM_SPRINTS + 1)}

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

total_cerradas      = sum(conteo.values())
sprints_con_hu      = [n for n in conteo if conteo[n] > 0]
num_sprints_activos = len(sprints_con_hu)
promedio            = round(total_cerradas / num_sprints_activos, 1) if num_sprints_activos else 0
fecha               = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

# Filas de la tabla
filas_html = ""
for n in range(1, NUM_SPRINTS + 1):
    color = "#1a2a3a" if n % 2 == 0 else "#162030"
    filas_html += f"""
        <tr style="background:{color}">
            <td>Sprint {n}</td>
            <td>{conteo[n]}</td>
        </tr>"""

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <title>Reporte HU por Sprint — MedTrack</title>
  <style>
    body {{
      margin: 0; padding: 2rem;
      background: #0F1B2D;
      font-family: 'Segoe UI', sans-serif;
      color: #E2EAF4;
    }}
    .tarjeta {{
      background: #162030;
      border: 1px solid #243447;
      border-radius: 16px;
      max-width: 700px;
      margin: 0 auto;
      padding: 2rem;
      box-shadow: 0 32px 80px rgba(0,0,0,.5);
    }}
    .marca {{
      display: flex; align-items: center; gap: .6rem; margin-bottom: 1.5rem;
    }}
    .marca-icono {{
      width: 36px; height: 36px; background: #2DD4BF;
      border-radius: 10px; display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem;
    }}
    .marca-nombre {{
      font-size: 1.4rem; font-weight: 700; color: #E2EAF4;
    }}
    h1 {{
      font-size: 1.5rem; margin: 0 0 .3rem; color: #E2EAF4;
    }}
    .subtitulo {{
      color: #7A95B0; font-size: .88rem; margin-bottom: 1.5rem;
    }}
    table {{
      width: 100%; border-collapse: collapse; margin-bottom: 1rem;
    }}
    thead th {{
      background: #1E2D3D; color: #2DD4BF;
      padding: .8rem 1rem; text-align: left;
      font-size: .78rem; text-transform: uppercase; letter-spacing: .06em;
      border-bottom: 1px solid #243447;
    }}
    tbody td {{
      padding: .75rem 1rem; border-bottom: 1px solid #243447;
      font-size: .9rem;
    }}
    .resumen {{
      display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;
    }}
    .card {{
      background: #1E2D3D; border: 1px solid #243447;
      border-radius: 12px; padding: 1rem 1.5rem; flex: 1; min-width: 140px;
    }}
    .card-valor {{
      font-size: 2rem; font-weight: 700; color: #2DD4BF;
    }}
    .card-label {{
      font-size: .78rem; color: #7A95B0; margin-top: .2rem;
    }}
    .warning {{
      background: rgba(244,114,106,.1); border: 1px solid #F4726A;
      color: #F4726A; border-radius: 10px; padding: .8rem 1rem;
      font-size: .85rem; margin-top: 1rem;
    }}
    .footer {{
      text-align: center; color: #4A6278; font-size: .78rem; margin-top: 1.5rem;
    }}
    tr:last-child td {{ border-bottom: none; }}
  </style>
</head>
<body>
  <div class="tarjeta">
    <div class="marca">
      <div class="marca-icono">💊</div>
      <span class="marca-nombre">MedTrack</span>
    </div>

    <h1>HU Cerradas por Sprint</h1>
    <p class="subtitulo">Repositorio: {repo}</p>

    <div class="resumen">
      <div class="card">
        <div class="card-valor">{total_cerradas}</div>
        <div class="card-label">Total HU cerradas</div>
      </div>
      <div class="card">
        <div class="card-valor">{promedio}</div>
        <div class="card-label">Promedio HU por sprint</div>
      </div>
      <div class="card">
        <div class="card-valor">{num_sprints_activos}</div>
        <div class="card-label">Sprints con HU</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Sprint</th>
          <th>HU Cerradas</th>
        </tr>
      </thead>
      <tbody>
        {filas_html}
      </tbody>
    </table>
    <div class="footer">
    </div>
  </div>
</body>
</html>"""

with open("/tmp/reporte.html", "w") as f:
    f.write(html)

print(f"Reporte generado — Total: {total_cerradas} HU, Promedio: {promedio} HU/sprint")