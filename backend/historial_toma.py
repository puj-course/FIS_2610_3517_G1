from datetime import datetime

class HistorialToma:
    """
    Representa el registro de una toma de medicamento realizada (o no) por un paciente.
    Se construye usando HistorialTomaBuilder, nunca directamente.
    """
    UMBRAL_A_TIEMPO_MINUTOS = 30  # si se tomó dentro de 30 min de la hora programada = a tiempo

    def __init__(
        self,
        paciente_id: int,
        medicamento_id: int,
        fecha_programada: str,
        recordatorio_id: int | None = None,
        fecha_hora_toma: str | None = None,
        diferencia_minutos: float | None = None,
        estado: str = "omitida",
        observaciones: str | None = None
    ):
        self.paciente_id        = paciente_id
        self.medicamento_id     = medicamento_id
        self.recordatorio_id    = recordatorio_id
        self.fecha_programada   = fecha_programada
        self.fecha_hora_toma    = fecha_hora_toma
        self.diferencia_minutos = diferencia_minutos
        self.estado             = estado
        self.observaciones      = observaciones

    def to_dict(self) -> dict:
        return {
            "paciente_id":        self.paciente_id,
            "medicamento_id":     self.medicamento_id,
            "recordatorio_id":    self.recordatorio_id,
            "fecha_programada":   self.fecha_programada,
            "fecha_hora_toma":    self.fecha_hora_toma,
            "diferencia_minutos": self.diferencia_minutos,
            "estado":             self.estado,
            "observaciones":      self.observaciones,
        }

    @staticmethod
    def calcular_estado(fecha_programada: str, fecha_hora_toma: str | None) -> tuple[str, float | None]:
        """
        Calcula el estado y la diferencia en minutos entre la hora programada y la real.
        Retorna (estado, diferencia_minutos).
        """
        if fecha_hora_toma is None:
            return "omitida", None

        try:
            fmt = "%Y-%m-%d %H:%M:%S"
            programada = datetime.strptime(fecha_programada, fmt)
            tomada     = datetime.strptime(fecha_hora_toma,   fmt)
        except ValueError:
            return "omitida", None

        diferencia = (tomada - programada).total_seconds() / 60  # puede ser negativa si se tomó antes

        if abs(diferencia) <= HistorialToma.UMBRAL_A_TIEMPO_MINUTOS:
            return "a_tiempo", round(diferencia, 2)
        return "tarde", round(diferencia, 2)
    
    class HistorialTomaBuilder:
        """
        Patrón Builder para construir objetos HistorialToma paso a paso.
        Garantiza que el estado y la diferencia se calculen automáticamente.
        """

        def __init__(self):
            self._paciente_id      = None
            self._medicamento_id   = None
            self._recordatorio_id  = None
            self._fecha_programada = None
            self._fecha_hora_toma  = None
            self._observaciones    = None

        def set_paciente(self, paciente_id: int) -> "HistorialTomaBuilder":
            self._paciente_id = paciente_id
            return self

        def set_medicamento(self, medicamento_id: int) -> "HistorialTomaBuilder":
            self._medicamento_id = medicamento_id
            return self

        def set_recordatorio(self, recordatorio_id: int | None) -> "HistorialTomaBuilder":
            self._recordatorio_id = recordatorio_id
            return self

        def set_fecha_programada(self, fecha_programada: str) -> "HistorialTomaBuilder":
            self._fecha_programada = fecha_programada
            return self

        def set_fecha_hora_toma(self, fecha_hora_toma: str | None) -> "HistorialTomaBuilder":
            self._fecha_hora_toma = fecha_hora_toma
            return self

        def set_observaciones(self, observaciones: str | None) -> "HistorialTomaBuilder":
            self._observaciones = observaciones
            return self

        def build(self) -> HistorialToma:
            """
            Construye el objeto HistorialToma calculando automáticamente
            el estado y la diferencia de tiempo.
            Lanza ValueError si faltan campos obligatorios.
            """
            if not self._paciente_id:
                raise ValueError("paciente_id es obligatorio")
            if not self._medicamento_id:
                raise ValueError("medicamento_id es obligatorio")
            if not self._fecha_programada:
                raise ValueError("fecha_programada es obligatoria")

            estado, diferencia = HistorialToma.calcular_estado(
                self._fecha_programada,
                self._fecha_hora_toma
            )

            return HistorialToma(
                paciente_id        = self._paciente_id,
                medicamento_id     = self._medicamento_id,
                recordatorio_id    = self._recordatorio_id,
                fecha_programada   = self._fecha_programada,
                fecha_hora_toma    = self._fecha_hora_toma,
                diferencia_minutos = diferencia,
                estado             = estado,
                observaciones      = self._observaciones
            )