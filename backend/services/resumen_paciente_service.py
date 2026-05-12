from datetime import datetime
from bson import ObjectId

from backend.database import pacientes_col, medicamentos_col, tomas_col


class ResumenPacienteService:
    def obtener_paciente(self, paciente_id: str):
        try:
            paciente = pacientes_col.find_one({"_id": ObjectId(paciente_id)})
        except Exception:
            paciente = pacientes_col.find_one({"id": paciente_id})

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
            "observaciones_adicionales": paciente.get("observaciones_adicionales", ""),
        }

    def obtener_medicamentos_activos(self, paciente_id: str):
        medicamentos = list(
            medicamentos_col.find({"paciente_id": str(paciente_id)})
        )

        resultado = []

        for medicamento in medicamentos:
            activo = medicamento.get("activo", True)
            estado = str(medicamento.get("estado", "activo")).lower()

            if activo is False or activo == 0 or estado in {"inactivo", "suspendido", "finalizado"}:
                continue

            resultado.append({
                "id": str(medicamento.get("_id", medicamento.get("id", ""))),
                "nombre": medicamento.get("nombre", ""),
                "dosis": medicamento.get("dosis", ""),
                "frecuencia": medicamento.get("frecuencia", ""),
                "horario": medicamento.get("horario", ""),
                "fecha_inicio": medicamento.get("fecha_inicio", ""),
                "fecha_fin": medicamento.get("fecha_fin", ""),
                "observaciones": medicamento.get("observaciones", ""),
                "paciente_id": medicamento.get("paciente_id", ""),
            })

        resultado.sort(key=lambda item: item.get("nombre", ""))
        return resultado

    def obtener_historial_formateado(self, paciente_id: str):
        tomas = list(
            tomas_col.find({"paciente_id": str(paciente_id)})
        )

        historial = []

        for toma in tomas:
            medicamento_id = toma.get("medicamento_id")
            medicamento_nombre = toma.get("nombre", toma.get("medicamento_nombre", ""))

            if medicamento_id and not medicamento_nombre:
                try:
                    medicamento = medicamentos_col.find_one({"_id": ObjectId(medicamento_id)})
                except Exception:
                    medicamento = medicamentos_col.find_one({"id": medicamento_id})

                if medicamento:
                    medicamento_nombre = medicamento.get("nombre", "")

            fecha_programada = toma.get("fecha_programada", "")
            fecha_hora_toma = toma.get("fecha_hora_toma")

            fecha = toma.get("fecha", "")
            hora_programada = toma.get("hora_programada", "")
            hora_tomada = toma.get("hora_tomada")

            if fecha_programada:
                partes = str(fecha_programada).split(" ")
                fecha = fecha or partes[0]
                hora_programada = hora_programada or (
                    partes[1] if len(partes) > 1 else ""
                )

            if fecha_hora_toma:
                partes_toma = str(fecha_hora_toma).split(" ")
                hora_tomada = (
                    partes_toma[1]
                    if len(partes_toma) > 1
                    else str(fecha_hora_toma)
                )

            historial.append({
                "id": str(toma.get("_id", toma.get("id", ""))),
                "paciente_id": toma.get("paciente_id", str(paciente_id)),
                "medicamento_id": medicamento_id,
                "recordatorio_id": toma.get("recordatorio_id"),
                "medicamento": medicamento_nombre,
                "medicamento_nombre": medicamento_nombre,
                "fecha": fecha,
                "hora_programada": hora_programada,
                "hora_tomada": hora_tomada,
                "hora_tomado": hora_tomada,
                "fecha_programada": fecha_programada,
                "fecha_hora_toma": fecha_hora_toma,
                "diferencia_minutos": toma.get("diferencia_minutos"),
                "estado": toma.get("estado", "pendiente"),
                "observaciones": toma.get("observaciones", ""),
            })

        historial.sort(key=lambda item: item.get("fecha_programada", ""))
        return historial

    def _calcular_tomas_esperadas(self, medicamentos):
        try:
            formato_fecha = "%m/%d/%Y"
            total = 0
            hoy = datetime.today().date()

            for medicamento in medicamentos:
                fecha_inicio_str = medicamento.get("fecha_inicio", "")
                fecha_fin_str = medicamento.get("fecha_fin", "")

                if not fecha_inicio_str:
                    continue

                inicio = datetime.strptime(fecha_inicio_str, formato_fecha).date()
                fin = (
                    datetime.strptime(fecha_fin_str, formato_fecha).date()
                    if fecha_fin_str
                    else hoy
                )

                dias = (min(fin, hoy) - inicio).days + 1

                if dias < 1:
                    continue

                horarios = [
                    horario.strip()
                    for horario in medicamento.get("horario", "").split(",")
                    if horario.strip()
                ]

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
        historial = self.obtener_historial_formateado(paciente_id)

        tomas_realizadas = sum(
            1 for toma in historial
            if toma.get("estado") in ["tomado", "tomada", "a_tiempo", "tarde"]
        )

        tomas_omitidas = sum(
            1 for toma in historial
            if toma.get("estado") == "omitida"
        )

        tomas_pendientes = sum(
            1 for toma in historial
            if toma.get("estado") == "pendiente"
        )

        total_esperado = self._calcular_tomas_esperadas(medicamentos)
        total_para_porcentaje = total_esperado if total_esperado else len(historial)

        porcentaje = (
            round((tomas_realizadas / total_para_porcentaje) * 100, 1)
            if total_para_porcentaje > 0
            else 0
        )

        cumplimiento = {
            "total_tomas": len(historial),
            "total_esperado": total_esperado if total_esperado else len(historial),
            "tomas_realizadas": tomas_realizadas,
            "tomas_omitidas": tomas_omitidas,
            "tomas_pendientes": tomas_pendientes,
            "porcentaje": porcentaje,
            "porcentaje_cumplimiento": porcentaje,
        }

        return {
            "paciente": {
                "id": paciente["id"],
                "nombres": paciente["nombres"],
                "apellidos": paciente["apellidos"],
                "tipo_documento": paciente["tipo_documento"],
                "numero_documento": paciente["numero_documento"],
                "telefono_contacto": paciente["telefono_contacto"],
                "eps_aseguradora": paciente["eps_aseguradora"],
                "diagnostico_principal": paciente["diagnostico_principal"],
            },
            "medicamentos_activos": medicamentos,
            "historial": historial,
            "cumplimiento": cumplimiento,
            "alertas": [],
        }