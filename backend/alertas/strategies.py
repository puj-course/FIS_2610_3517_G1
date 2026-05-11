from backend.database import medicamentos_col


class AlertaStrategy:
    def evaluar(self, data: dict, conn=None) -> dict | None:
        raise NotImplementedError("Cada estrategia debe implementar el método evaluar().")


class MedicamentoDuplicadoStrategy(AlertaStrategy):
    def evaluar(self, data: dict, conn=None) -> dict | None:
        paciente_id = str(data.get("paciente_id", "")).strip()

        nombre = (
            data.get("nombre")
            or data.get("nombre_medicamento")
            or ""
        ).strip().lower()

        if not paciente_id or not nombre:
            return None

        resultado = medicamentos_col.find_one({
            "paciente_id": paciente_id,
            "nombre": nombre
        })

        if resultado:
            return {
                "tipo": "medicamento_duplicado",
                "mensaje": f"El paciente ya tiene registrado el medicamento {nombre}.",
                "nivel": "alta"
            }

        return None


class DosisDuplicadaStrategy(AlertaStrategy):
    def evaluar(self, data: dict, conn=None) -> dict | None:
        paciente_id = str(data.get("paciente_id", "")).strip()
        dosis = str(data.get("dosis", "")).strip().lower()

        if not paciente_id or not dosis:
            return None

        resultado = medicamentos_col.find_one({
            "paciente_id": paciente_id,
            "dosis": dosis
        })

        if resultado:
            return {
                "tipo": "dosis_duplicada",
                "mensaje": f"El paciente ya tiene un medicamento con la dosis {dosis}.",
                "nivel": "alta"
            }

        return None


class RecordatorioSeguimientoStrategy(AlertaStrategy):
    def evaluar(self, data: dict, conn=None) -> dict | None:
        activo = int(data.get("activo", 1))

        if activo == 1:
            return {
                "tipo": "seguimiento_recordatorio",
                "mensaje": f"Se creó un recordatorio activo para el medicamento {data.get('medicamento_id')}.",
                "nivel": "media"
            }

        return None


class AlertaContext:
    def _init_(self, strategy: AlertaStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: AlertaStrategy):
        self.strategy = strategy

    def ejecutar(self, data: dict, conn=None) -> dict | None:
        return self.strategy.evaluar(data, conn)