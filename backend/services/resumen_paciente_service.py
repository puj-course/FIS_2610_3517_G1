from backend.models import get_connection, obtener_historial_tomas
from backend.decorators.historial import (
    HistorialTomas,
    CumplimientoDecorator,
    AlertasDecorator
)


class ResumenPacienteService:
    def obtener_paciente(self, paciente_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM pacientes
            WHERE id = ?
        """, (paciente_id,))

        paciente = cursor.fetchone()
        conn.close()

        if not paciente:
            return None

        return dict(paciente)

    def obtener_medicamentos_activos(self, paciente_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM medicamentos
            WHERE paciente_id = ?
        """, (paciente_id,))

        medicamentos = cursor.fetchall()
        conn.close()

        return [dict(m) for m in medicamentos]

    def obtener_historial_formateado(self, paciente_id: int):
        tomas = obtener_historial_tomas(paciente_id)

        historial = []

        for t in tomas:
            historial.append({
                "id": t["id"],
                "paciente_id": t["paciente_id"],
                "medicamento_id": t["medicamento_id"],
                "medicamento": t["nombre"],
                "fecha": t["fecha"],
                "hora_programada": t["hora_programada"],
                "hora_tomado": t["hora_tomada"],
                "estado": t["estado"],
                "observaciones": t["observaciones"]
            })

        return historial

    def construir_resumen(self, paciente_id: int):
        paciente = self.obtener_paciente(paciente_id)

        if not paciente:
            raise LookupError("Paciente no encontrado")

        medicamentos = self.obtener_medicamentos_activos(paciente_id)
        historial_base = self.obtener_historial_formateado(paciente_id)

        historial = HistorialTomas(historial_base)
        historial = CumplimientoDecorator(historial)
        historial = AlertasDecorator(historial)

        historial_enriquecido = historial.obtener_datos()

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