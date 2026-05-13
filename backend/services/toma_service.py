from typing import Any, Dict, Optional
from datetime import datetime, timezone

from bson import ObjectId

from backend.database import (
    pacientes_col,
    medicamentos_col,
    recordatorios_col,
    tomas_col,
)
from backend.historial_toma import HistorialTomaBuilder

try:
    from backend.alertas.bootstrap import publisher
except Exception:
    publisher = None


class TomaService:

    def registrar_toma(
        self,
        paciente_id: str,
        medicamento_id: str,
        fecha_programada: str,
        fecha_hora_toma: str,
        estado: str = "tomada",
        observaciones: Optional[str] = None,
    ) -> Dict[str, Any]:

        self._validar_campos_obligatorios(
            paciente_id=paciente_id,
            medicamento_id=medicamento_id,
            fecha_programada=fecha_programada,
            fecha_hora_toma=fecha_hora_toma,
            estado=estado,
        )

        paciente_id = str(paciente_id)
        medicamento_id = str(medicamento_id)

        paciente = self._obtener_paciente(paciente_id)
        if not paciente:
            raise LookupError("El paciente no existe")

        medicamento = self._obtener_medicamento(medicamento_id)
        if not medicamento:
            raise LookupError("El medicamento no existe")

        paciente_medicamento_id = str(medicamento.get("paciente_id", ""))
        if paciente_medicamento_id and paciente_medicamento_id != paciente_id:
            raise ValueError("El medicamento no pertenece al paciente")

        toma = (
            HistorialTomaBuilder()
            .set_paciente(paciente_id)
            .set_medicamento(medicamento_id)
            .set_recordatorio(None)
            .set_fecha_programada(fecha_programada)
            .set_fecha_hora_toma(fecha_hora_toma)
            .set_observaciones(observaciones)
            .build()
        )

        documento = {
            "paciente_id": toma.paciente_id,
            "medicamento_id": toma.medicamento_id,
            "recordatorio_id": None,
            "fecha_programada": toma.fecha_programada,
            "fecha_hora_toma": toma.fecha_hora_toma,
            "diferencia_minutos": toma.diferencia_minutos,
            "estado": toma.estado,
            "observaciones": toma.observaciones,
            "created_at": datetime.now(timezone.utc),
        }

        resultado = tomas_col.insert_one(documento)
        toma_id = str(resultado.inserted_id)

        if publisher:
            publisher.notify({
                "type": "medication_taken",
                "toma_id": toma_id,
                **documento,
            })

        return {
            "ok": True,
            "mensaje": "Toma registrada correctamente",
            "toma_id": toma_id,
            "data": self._serializar_toma({
                "_id": resultado.inserted_id,
                **documento,
            }),
        }

    def obtener_tomas_del_dia(self, paciente_id, fecha: str):
        paciente_id = str(paciente_id)
        tomas = tomas_col.find({
            "paciente_id": paciente_id,
            "fecha_programada": {"$regex": f"^{fecha}"},
        }).sort("fecha_programada", -1)
        return [self._serializar_toma(toma) for toma in tomas]

    def obtener_historial(self, paciente_id):
        paciente_id = str(paciente_id)
        tomas = tomas_col.find({
            "paciente_id": paciente_id,
        }).sort("fecha_programada", -1)

        historial = []
        for toma in tomas:
            medicamento = self._obtener_medicamento(str(toma.get("medicamento_id")))
            estado_historial = self._normalizar_estado_historial(toma.get("estado"))
            fecha_programada = toma.get("fecha_programada", "")
            fecha_hora_toma = toma.get("fecha_hora_toma", "")

            historial.append({
                "id": str(toma.get("_id")),
                "paciente_id": toma.get("paciente_id"),
                "medicamento_id": toma.get("medicamento_id"),
                "medicamento_nombre": medicamento.get("nombre", "") if medicamento else "",
                "medicamento": medicamento.get("nombre", "") if medicamento else "",
                "recordatorio_id": None,
                "fecha": fecha_programada[:10] if fecha_programada else "",
                "hora_programada": fecha_programada[11:16] if len(fecha_programada) >= 16 else "",
                "hora_tomada": fecha_hora_toma[11:16] if len(fecha_hora_toma) >= 16 else "",
                "hora_tomado": fecha_hora_toma[11:16] if len(fecha_hora_toma) >= 16 else "",
                "fecha_programada": fecha_programada,
                "fecha_hora_toma": fecha_hora_toma,
                "diferencia_minutos": toma.get("diferencia_minutos"),
                "estado": estado_historial,
                "observaciones": toma.get("observaciones"),
            })

        return historial

    def _validar_campos_obligatorios(
        self,
        paciente_id,
        medicamento_id,
        fecha_programada: str,
        fecha_hora_toma: str,
        estado: str,
    ) -> None:
        if not paciente_id:
            raise ValueError("El paciente_id es obligatorio")
        if not medicamento_id:
            raise ValueError("El medicamento_id es obligatorio")
        if not fecha_programada or not str(fecha_programada).strip():
            raise ValueError("La fecha_programada es obligatoria")
        if not fecha_hora_toma or not str(fecha_hora_toma).strip():
            raise ValueError("La fecha_hora_toma es obligatoria")
        if not estado or not str(estado).strip():
            raise ValueError("El estado es obligatorio")

    def _obtener_paciente(self, paciente_id: str):
        try:
            paciente = pacientes_col.find_one({"_id": ObjectId(paciente_id)})
            if paciente:
                return paciente
        except Exception:
            pass
        return pacientes_col.find_one({"id": paciente_id})

    def _obtener_medicamento(self, medicamento_id: str):
        try:
            medicamento = medicamentos_col.find_one({"_id": ObjectId(medicamento_id)})
            if medicamento:
                return medicamento
        except Exception:
            pass
        return medicamentos_col.find_one({"id": medicamento_id})

    def _serializar_toma(self, toma: dict) -> dict:
        toma["id"] = str(toma.get("_id"))
        toma.pop("_id", None)
        if "created_at" in toma and toma["created_at"]:
            toma["created_at"] = str(toma["created_at"])
        return toma

    def _normalizar_estado_historial(self, estado: str) -> str:
        if estado == "a_tiempo":
            return "tomado"
        if estado in ["tarde", "atrasada", "atrasado", "omitida"]:
            return "atrasado"
        return estado or "pendiente"