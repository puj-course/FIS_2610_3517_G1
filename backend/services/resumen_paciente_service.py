from bson import ObjectId
from backend.database import pacientes_col, medicamentos_col, tomas_col


class ResumenPacienteService:
    def obtener_paciente(self, paciente_id: str):
        try:
            paciente = pacientes_col.find_one({"_id": ObjectId(paciente_id)})
        except Exception:
            paciente = pacientes_col.find_one({"id": paciente_id})
        return paciente

    def obtener_medicamentos_activos(self, paciente_id: str):
        try:
            oid = ObjectId(paciente_id)
            meds = list(medicamentos_col.find({"paciente_id": str(oid)}))
            if not meds:
                meds = list(medicamentos_col.find({"paciente_id": paciente_id}))
        except Exception:
            meds = list(medicamentos_col.find({"paciente_id": paciente_id}))
        return meds

    def obtener_historial_formateado(self, paciente_id: str):
        try:
            oid = ObjectId(paciente_id)
            tomas = list(tomas_col.find({"paciente_id": str(oid)}))
            if not tomas:
                tomas = list(tomas_col.find({"paciente_id": paciente_id}))
        except Exception:
            tomas = list(tomas_col.find({"paciente_id": paciente_id}))

        historial = []
        for t in tomas:
            historial.append({
                "id": str(t.get("_id", "")),
                "paciente_id": paciente_id,
                "medicamento_id": str(t.get("medicamento_id", "")),
                "medicamento": t.get("nombre", t.get("medicamento_nombre", "")),
                "medicamento_nombre": t.get("nombre", t.get("medicamento_nombre", "")),
                "fecha": t.get("fecha", ""),
                "hora_programada": t.get("hora_programada", ""),
                "hora_tomada": t.get("hora_tomada", ""),
                "estado": t.get("estado", "pendiente"),
                "observaciones": t.get("observaciones", ""),
            })
        return historial

    def construir_resumen(self, paciente_id: str):
        paciente = self.obtener_paciente(paciente_id)
        if not paciente:
            raise LookupError("Paciente no encontrado")

        medicamentos = self.obtener_medicamentos_activos(paciente_id)
        historial = self.obtener_historial_formateado(paciente_id)

        tomas_realizadas = sum(1 for t in historial if t["estado"] in ["tomado", "tomada", "a_tiempo", "tarde"])
        tomas_omitidas   = sum(1 for t in historial if t["estado"] == "omitida")
        tomas_pendientes = sum(1 for t in historial if t["estado"] == "pendiente")
        tomas_tarde      = sum(1 for t in historial if t["estado"] == "tarde")
        total            = len(historial)
        porcentaje       = round((tomas_realizadas / total * 100), 1) if total > 0 else 0

        return {
            "paciente": {
                "id": str(paciente.get("_id", "")),
                "nombres": paciente.get("nombres", ""),
                "apellidos": paciente.get("apellidos", ""),
                "tipo_documento": paciente.get("tipo_documento", ""),
                "numero_documento": paciente.get("numero_documento", ""),
                "telefono_contacto": paciente.get("telefono_contacto", ""),
                "eps_aseguradora": paciente.get("eps_aseguradora", ""),
                "diagnostico_principal": paciente.get("diagnostico_principal", ""),
            },
            "medicamentos_activos": medicamentos,
            "historial": historial,
            "cumplimiento": {
                "total_tomas": total,
                "tomas_realizadas": tomas_realizadas,
                "porcentaje": porcentaje,
            },
            "alertas": [],
        }