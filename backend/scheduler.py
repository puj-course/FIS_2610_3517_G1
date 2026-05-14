import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId
from backend.database import medicamentos_col, tomas_col, usuarios_col, pacientes_col
from backend.services.sms_service import enviar_sms

ya_enviados = set()

def verificar_tomas():
    ahora = datetime.now()
    h = ahora.hour
    m = ahora.minute
    minutos_ahora = h * 60 + m
    print(f"[Scheduler] Revisando tomas - hora actual: {h}:{m:02d} ({minutos_ahora} min)")

    medicamentos = list(medicamentos_col.find({}))
    print(f"[Scheduler] Medicamentos encontrados: {len(medicamentos)}")

    for med in medicamentos:
        horarios_raw = med.get("horarios", med.get("horario", ""))
        if isinstance(horarios_raw, list):
            horarios = horarios_raw
        else:
            horarios = [x.strip() for x in horarios_raw.split(",") if x.strip()]

        if not horarios:
            continue

        paciente_id = str(med.get("paciente_id", ""))
        nombre_med = med.get("nombre_medicamento", med.get("nombre", "medicamento"))

        try:
            paciente = pacientes_col.find_one({"_id": ObjectId(paciente_id)})
        except:
            paciente = None

        if not paciente:
            print(f"[Scheduler] Paciente no encontrado: {paciente_id}")
            continue

        nombre_paciente = f"{paciente.get('nombres', '')} {paciente.get('apellidos', '')}".strip()

        cuidador_id = str(paciente.get("cuidador_id", ""))
        if not cuidador_id:
            print(f"[Scheduler] Paciente {nombre_paciente} sin cuidador_id")
            continue

        try:
            cuidador = usuarios_col.find_one({"_id": ObjectId(cuidador_id)})
        except:
            print(f"[Scheduler] Error buscando cuidador: {cuidador_id}")
            continue

        if not cuidador:
            print(f"[Scheduler] Cuidador no encontrado: {cuidador_id}")
            continue

        telefono = cuidador.get("telefono", "")
        print(f"[Scheduler] Cuidador: {cuidador.get('nombre')} | Tel: {telefono}")

        if not telefono:
            print(f"[Scheduler] Sin telefono")
            continue

        fecha_hoy = ahora.strftime("%Y-%m-%d")
        med_id = str(med.get("_id", ""))

        for hora in horarios:
            try:
                hh, mm = hora.split(":")
                minutos_med = int(hh) * 60 + int(mm)
            except:
                print(f"[Scheduler] Hora invalida: {hora}")
                continue

            diff = minutos_med - minutos_ahora
            print(f"[Scheduler] {nombre_med} | Hora: {hora} | diff: {diff} min")

            clave_rec = f"rec_{med_id}_{hora}_{fecha_hoy}"
            clave_per = f"per_{med_id}_{hora}_{fecha_hoy}"

            toma_hoy = tomas_col.find_one({
                "medicamento_id": med_id,
                "fecha_programada": {"$regex": f"^{fecha_hoy}"},
                "estado": {"$in": ["tomada", "a_tiempo", "tarde"]}
            })

            if 10 <= diff <= 20 and clave_rec not in ya_enviados:
                ya_enviados.add(clave_rec)
                print(f"[Scheduler] Enviando recordatorio SMS a {telefono}")
                enviar_sms(
                    telefono,
                    f"MedTrack: Recordatorio - {nombre_paciente} debe tomar {nombre_med} en 15 minutos (a las {hora})."
                )

            if -10 <= diff <= -4 and not toma_hoy and clave_per not in ya_enviados:
                ya_enviados.add(clave_per)
                print(f"[Scheduler] Enviando alerta SMS a {telefono}")
                enviar_sms(
                    telefono,
                    f"MedTrack: ALERTA - {nombre_paciente} no ha registrado la toma de {nombre_med} que era a las {hora}."
                )

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        verificar_tomas,
        'interval',
        minutes=1,
        misfire_grace_time=30
    )
    scheduler.start()
    print("Scheduler de alertas SMS iniciado.")
    return scheduler