from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from backend.database import pacientes_col, medicamentos_col, tomas_col


FORMATO_FECHA = "%m/%d/%Y"
ESTADOS_TOMA_REALIZADA = {"tomado", "tomada", "a_tiempo", "tarde"}
ESTADOS_MEDICAMENTO_INACTIVO = {"inactivo", "suspendido", "finalizado"}


class ResumenPacienteService:
    def obtener_paciente(self, paciente_id: str):
        paciente = self._buscar_paciente(paciente_id)

        if not paciente:
            return None

        return self._serializar_paciente_completo(paciente)

    def obtener_medicamentos_activos(self, paciente_id: str):
        medicamentos = list(
            medicamentos_col.find({"paciente_id": str(paciente_id)})
        )

        resultado = [
            self._serializar_medicamento(medicamento)
            for medicamento in medicamentos
            if self._medicamento_esta_activo(medicamento)
        ]

        resultado.sort(key=lambda item: item.get("nombre", ""))
        return resultado

    def obtener_historial_formateado(self, paciente_id: str):
        tomas = list(tomas_col.find({"paciente_id": str(paciente_id)}))

        historial = [
            self._serializar_toma(toma, paciente_id)
            for toma in tomas
        ]

        historial.sort(key=lambda item: item.get("fecha_programada", ""))
        return historial

    def construir_resumen(self, paciente_id: str):
        paciente = self.obtener_paciente(paciente_id)

        if not paciente:
            raise LookupError("Paciente no encontrado")

        medicamentos = self.obtener_medicamentos_activos(paciente_id)
        historial = self.obtener_historial_formateado(paciente_id)
        cumplimiento = self._construir_cumplimiento(medicamentos, historial)

        return {
            "paciente": self._serializar_paciente_resumen(paciente),
            "medicamentos_activos": medicamentos,
            "historial": historial,
            "cumplimiento": cumplimiento,
            "alertas": [],
        }

    def _buscar_paciente(self, paciente_id: str):
        try:
            paciente = pacientes_col.find_one({"_id": ObjectId(paciente_id)})
            if paciente:
                return paciente
        except (InvalidId, TypeError):
            pass

        return pacientes_col.find_one({"id": paciente_id})

    def _buscar_medicamento(self, medicamento_id: str):
        if not medicamento_id:
            return None

        try:
            medicamento = medicamentos_col.find_one({"_id": ObjectId(medicamento_id)})
            if medicamento:
                return medicamento
        except (InvalidId, TypeError):
            pass

        return medicamentos_col.find_one({"id": medicamento_id})

    def _serializar_paciente_completo(self, paciente: dict) -> dict:
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

    def _serializar_paciente_resumen(self, paciente: dict) -> dict:
        return {
            "id": paciente["id"],
            "nombres": paciente["nombres"],
            "apellidos": paciente["apellidos"],
            "tipo_documento": paciente["tipo_documento"],
            "numero_documento": paciente["numero_documento"],
            "telefono_contacto": paciente["telefono_contacto"],
            "eps_aseguradora": paciente["eps_aseguradora"],
            "diagnostico_principal": paciente["diagnostico_principal"],
        }

    def _medicamento_esta_activo(self, medicamento: dict) -> bool:
        activo = medicamento.get("activo", True)
        estado = str(medicamento.get("estado", "activo")).lower()

        if activo is False or activo == 0:
            return False

        return estado not in ESTADOS_MEDICAMENTO_INACTIVO

    def _serializar_medicamento(self, medicamento: dict) -> dict:
        return {
            "id": str(medicamento.get("_id", medicamento.get("id", ""))),
            "nombre": medicamento.get("nombre", ""),
            "dosis": medicamento.get("dosis", ""),
            "frecuencia": medicamento.get("frecuencia", ""),
            "horario": medicamento.get("horario", ""),
            "fecha_inicio": medicamento.get("fecha_inicio", ""),
            "fecha_fin": medicamento.get("fecha_fin", ""),
            "observaciones": medicamento.get("observaciones", ""),
            "paciente_id": medicamento.get("paciente_id", ""),
        }

    def _obtener_nombre_medicamento(self, toma: dict) -> str:
        nombre_guardado = toma.get("nombre", toma.get("medicamento_nombre", ""))

        if nombre_guardado:
            return nombre_guardado

        medicamento = self._buscar_medicamento(toma.get("medicamento_id"))

        if not medicamento:
            return ""

        return medicamento.get("nombre", "")

    def _extraer_fecha_hora_programada(self, toma: dict) -> tuple[str, str]:
        fecha = toma.get("fecha", "")
        hora_programada = toma.get("hora_programada", "")
        fecha_programada = str(toma.get("fecha_programada", ""))

        if not fecha_programada:
            return fecha, hora_programada

        partes = fecha_programada.split(" ")
        fecha = fecha or partes[0]
        hora_programada = hora_programada or self._obtener_segunda_parte(partes)

        return fecha, hora_programada

    def _extraer_hora_tomada(self, toma: dict):
        hora_tomada = toma.get("hora_tomada")
        fecha_hora_toma = toma.get("fecha_hora_toma")

        if not fecha_hora_toma:
            return hora_tomada

        partes = str(fecha_hora_toma).split(" ")
        return self._obtener_segunda_parte(partes) or str(fecha_hora_toma)

    def _obtener_segunda_parte(self, partes: list[str]) -> str:
        return partes[1] if len(partes) > 1 else ""

    def _serializar_toma(self, toma: dict, paciente_id: str) -> dict:
        fecha, hora_programada = self._extraer_fecha_hora_programada(toma)
        hora_tomada = self._extraer_hora_tomada(toma)
        medicamento_nombre = self._obtener_nombre_medicamento(toma)

        return {
            "id": str(toma.get("_id", toma.get("id", ""))),
            "paciente_id": toma.get("paciente_id", str(paciente_id)),
            "medicamento_id": toma.get("medicamento_id"),
            "recordatorio_id": toma.get("recordatorio_id"),
            "medicamento": medicamento_nombre,
            "medicamento_nombre": medicamento_nombre,
            "fecha": fecha,
            "hora_programada": hora_programada,
            "hora_tomada": hora_tomada,
            "hora_tomado": hora_tomada,
            "fecha_programada": toma.get("fecha_programada", ""),
            "fecha_hora_toma": toma.get("fecha_hora_toma"),
            "diferencia_minutos": toma.get("diferencia_minutos"),
            "estado": toma.get("estado", "pendiente"),
            "observaciones": toma.get("observaciones", ""),
        }

    def _parsear_fecha(self, fecha: str):
        if not fecha:
            return None

        try:
            return datetime.strptime(fecha, FORMATO_FECHA).date()
        except ValueError:
            return None

    def _obtener_horarios(self, medicamento: dict) -> list[str]:
        return [
            horario.strip()
            for horario in medicamento.get("horario", "").split(",")
            if horario.strip()
        ]

    def _calcular_dias_tratamiento(self, medicamento: dict):
        inicio = self._parsear_fecha(medicamento.get("fecha_inicio", ""))

        if not inicio:
            return 0

        hoy = datetime.today().date()
        fin = self._parsear_fecha(medicamento.get("fecha_fin", "")) or hoy
        dias = (min(fin, hoy) - inicio).days + 1

        return max(dias, 0)

    def _calcular_tomas_medicamento(self, medicamento: dict) -> int:
        dias = self._calcular_dias_tratamiento(medicamento)

        if dias < 1:
            return 0

        horarios = self._obtener_horarios(medicamento)
        tomas_por_dia = len(horarios) if horarios else 1

        return dias * tomas_por_dia

    def _calcular_tomas_esperadas(self, medicamentos):
        total = sum(
            self._calcular_tomas_medicamento(medicamento)
            for medicamento in medicamentos
        )

        return total if total > 0 else None

    def _contar_tomas_por_estado(self, historial: list[dict], estados: set[str]) -> int:
        return sum(
            1 for toma in historial
            if toma.get("estado") in estados
        )

    def _calcular_porcentaje_cumplimiento(
        self,
        tomas_realizadas: int,
        total_para_porcentaje: int,
    ) -> float:
        if total_para_porcentaje <= 0:
            return 0

        return round((tomas_realizadas / total_para_porcentaje) * 100, 1)

    def _construir_cumplimiento(
        self,
        medicamentos: list[dict],
        historial: list[dict],
    ) -> dict:
        tomas_realizadas = self._contar_tomas_por_estado(
            historial,
            ESTADOS_TOMA_REALIZADA,
        )
        tomas_omitidas = self._contar_tomas_por_estado(historial, {"omitida"})
        tomas_pendientes = self._contar_tomas_por_estado(historial, {"pendiente"})

        total_esperado = self._calcular_tomas_esperadas(medicamentos)
        total_tomas = len(historial)
        total_para_porcentaje = total_esperado or total_tomas
        porcentaje = self._calcular_porcentaje_cumplimiento(
            tomas_realizadas,
            total_para_porcentaje,
        )

        return {
            "total_tomas": total_tomas,
            "total_esperado": total_esperado or total_tomas,
            "tomas_realizadas": tomas_realizadas,
            "tomas_omitidas": tomas_omitidas,
            "tomas_pendientes": tomas_pendientes,
            "porcentaje": porcentaje,
            "porcentaje_cumplimiento": porcentaje,
        }