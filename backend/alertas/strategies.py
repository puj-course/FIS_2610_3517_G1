class AlertaStrategy:
    """
    Clase base para todas las estrategias de alerta.
    """

    def evaluar(self, data: dict, conn=None) -> dict | None:
        raise NotImplementedError("Cada estrategia debe implementar el método evaluar().")


class MedicamentoDuplicadoStrategy(AlertaStrategy):
    """
    Detecta si un paciente ya tiene registrado un medicamento con el mismo nombre.
    """

    def evaluar(self, data: dict, conn=None) -> dict | None:
        if conn is None:
            return None

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id
            FROM medicamentos
            WHERE paciente_id = ?
              AND LOWER(TRIM(nombre)) = LOWER(TRIM(?))
            """,
            (int(data["paciente_id"]), data["nombre"].strip())
        )

        resultado = cursor.fetchone()

        if resultado:
            return {
                "tipo": "medicamento_duplicado",
                "mensaje": f"El paciente ya tiene registrado el medicamento {data['nombre']}.",
                "nivel": "alta"
            }

        return None


class DosisDuplicadaStrategy(AlertaStrategy):
    """
    Detecta si el paciente ya tiene un medicamento con la misma dosis.
    """

    def evaluar(self, data: dict, conn=None) -> dict | None:
        if conn is None:
            return None

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id
            FROM medicamentos
            WHERE paciente_id = ?
              AND LOWER(TRIM(dosis)) = LOWER(TRIM(?))
            """,
            (int(data["paciente_id"]), data["dosis"].strip())
        )

        resultado = cursor.fetchone()

        if resultado:
            return {
                "tipo": "dosis_duplicada",
                "mensaje": f"El paciente ya tiene un medicamento con la dosis {data['dosis']}.",
                "nivel": "alta"
            }

        return None


class RecordatorioSeguimientoStrategy(AlertaStrategy):
    """
    Genera una alerta cuando se crea un recordatorio activo.
    """

    def evaluar(self, data: dict, conn=None) -> dict | None:
        activo = int(data.get("activo", 1))

        if activo == 1:
            return {
                "tipo": "seguimiento_recordatorio",
                "mensaje": f"Se creó un recordatorio activo para el medicamento {data['medicamento_id']}.",
                "nivel": "media"
            }

        return None


class AlertaContext:
    """
    Contexto que permite ejecutar diferentes estrategias dinámicamente.
    """

    def __init__(self, strategy: AlertaStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: AlertaStrategy):
        self.strategy = strategy

    def ejecutar(self, data: dict, conn=None) -> dict | None:
        return self.strategy.evaluar(data, conn)