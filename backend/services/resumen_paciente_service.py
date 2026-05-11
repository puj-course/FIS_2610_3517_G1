from bson import ObjectId
from datetime import datetime
from backend.database import pacientes_col, medicamentos_col, tomas_col

from backend.decorators.historial import (
    HistorialTomas,
    CumplimientoDecorator,
    AlertasDecorator
)


class ResumenPacienteService:
    def obtener_paciente(self, paciente_id: str):
        try:
            paciente = pacientes_col.find_one({
                "_id": ObjectId(paciente_id)
            })
        except Exception:
            paciente = pacientes_col.find_one({
                "id": paciente_id
            })

        if not paciente:
            return None

        return {
            "id": str(paciente.get("_id", paciente.get("id", ""))),
            "nombres": paciente.get("nombres", ""),
            "apellidos": paciente.get("apellidos", ""),
            "fecha_nacimiento": paciente.get("fecha_nacimiento", ""),
            "genero": paciente.get("genero", ""),
            "tipo_documento": paciente.get("tipo_documento", ""),
            "numero_documento": paciente.get("numero_documento", ""),
            "telefono_contacto": paciente.get("telefono_contacto", ""),
            "eps_aseguradora": paciente.get("eps_aseguradora", ""),
            "diagnostico_principal": paciente.get("diagnostico_principal", ""),
            "alergias_conocidas": paciente.get("alergias_conocidas", ""),
            "observaciones_adicionales": paciente.get("observaciones_adicionales", "")
        }

    def obtener_medicamentos_activos(self, paciente_id: str):
        medicamentos = list(
            medicamentos_col.find({
                "paciente_id": str(paciente_id)
            }).sort("nombre", 1)
        )

        resultado = []

        for m in medicamentos:
            resultado.append({
                "id": str(m.get("_id", m.get("id", ""))),
                "nombre": m.get("nombre", ""),
                "dosis": m.get("dosis", ""),
                "frecuencia": m.get("frecuencia", ""),
                "horario": m.get("horario", ""),
                "fecha_inicio": m.get("fecha_inicio", ""),
                "observaciones": m.get("observaciones", ""),
                "paciente_id": m.get("paciente_id", "")
            })

        return resultado

    def obtener_historial_formateado(self, paciente_id: str):
        tomas = list(
            tomas_col.find({
                "paciente_id": str(paciente_id)
            }).sort("fecha_programada", -1)
        )

        historial = []

        for t in tomas:
            medicamento_id = t.get("medicamento_id")
            medicamento_nombre = t.get("nombre", t.get("medicamento_nombre", ""))

            if medicamento_id and not medicamento_nombre:
                try:
                    medicamento = medicamentos_col.find_one({
                        "_id": ObjectId(medicamento_id)
                    })

                    if medicamento:
                        medicamento_nombre = medicamento.get("nombre", "")

                except Exception:
                    medicamento = medicamentos_col.find_one({
                        "id": medicamento_id
                    })

                    if medicamento:
                        medicamento_nombre = medicamento.get("nombre", "")

            fecha_programada = t.get("fecha_programada", "")
            fecha_hora_toma = t.get("fecha_hora_toma")

            fecha = t.get("fecha", "")
            hora_programada = t.get("hora_programada", "")
            hora_tomada = t.get("hora_tomada")

            if fecha_programada:
                partes = str(fecha_programada).split(" ")
                fecha = fecha or partes[0]
                hora_programada = hora_programada or (partes[1] if len(partes) > 1 else "")

            if fecha_hora_toma:
                partes_toma = str(fecha_hora_toma).split(" ")
                hora_tomada = partes_toma[1] if len(partes_toma) > 1 else str(fecha_hora_toma)

            historial.append({
                "id": str(t.get("_id", t.get("id", ""))),
                "paciente_id": t.get("paciente_id", str(paciente_id)),
                "medicamento_id": medicamento_id,
                "recordatorio_id": t.get("recordatorio_id"),

                "medicamento": medicamento_nombre,
                "medicamento_nombre": medicamento_nombre,

                "fecha": fecha,
                "hora_programada": hora_programada,

                "hora_tomada": hora_tomada,
                "hora_tomado": hora_tomada,

                "fecha_programada": fecha_programada,
                "fecha_hora_toma": fecha_hora_toma,

                "diferencia_minutos": t.get("diferencia_minutos"),
                "estado": t.get("estado", "pendiente"),
                "observaciones": t.get("observaciones", "")
            })

        return historial

    def _calcular_tomas_esperadas(self, medicamentos):
        try:
            fmt = "%m/%d/%Y"
            total = 0
            hoy = datetime.today().date()
            for m in medicamentos:
                fecha_inicio_str = m.get("fecha_inicio", "")
                fecha_fin_str = m.get("fecha_fin", "")
                if not fecha_inicio_str:
                    continue
                inicio = datetime.strptime(fecha_inicio_str, fmt).date()
                fin = datetime.strptime(fecha_fin_str, fmt).date() if fecha_fin_str else hoy
                dias = (min(fin, hoy) - inicio).days + 1
                if dias < 1:
                    continue
                horarios = [h.strip() for h in m.get("horario", "").split(",") if h.strip()]
                tomas_por_dia = len(horarios) if horarios else 1
                total += dias * tomas_por_dia
            return total if total > 0 else None
        except Exception:
            return None

    def construir_resumen(self, paciente_id: str):
        paciente = self.obtener_paciente(paciente_id)

        if not paciente:
            raise LookupError("Paciente no encontrado")

        medicamentos = self.obtener_medicamentos_activos(paciente_id)
        historial_base = self.obtener_historial_formateado(paciente_id)

        tomas_realizadas = sum(1 for t in historial if t["estado"] in ["tomado", "tomada", "a_tiempo", "tarde"])
        tomas_omitidas   = sum(1 for t in historial if t["estado"] == "omitida")
        tomas_pendientes = sum(1 for t in historial if t["estado"] == "pendiente")

        total_esperado = self._calcular_tomas_esperadas(medicamentos)
        total = total_esperado if total_esperado else len(historial)
        porcentaje = round((tomas_realizadas / total * 100), 1) if total > 0 else 0

        return {
            "paciente": {
                "id": paciente["id"],
                "nombres": paciente["nombres"],
                "apellidos": paciente["apellidos"],
                "tipo_documento": paciente["tipo_documento"],
                "numero_documento": paciente["numero_documento"],
                "telefono_contacto": paciente["telefono_contacto"],
                "eps_aseguradora": paciente["eps_aseguradora"],
                "diagnostico_principal": paciente["diagnostico_principal"]
            },
            "medicamentos_activos": medicamentos,
            "historial": historial_enriquecido.get("historial", []),
            "cumplimiento": historial_enriquecido.get("cumplimiento", {}),
            "alertas": historial_enriquecido.get("alertas", [])
        }