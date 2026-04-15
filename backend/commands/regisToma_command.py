#####################################################################################
#	Fichero para registrar la toma, implementación del patrón Command y representa
#	el Command como tal, puesto que representa la orden "registrar toma"
#
######################################################################################3

from backend.commands.comand_base import Command


class RegisToma_command(Command):
    """
    Command concreto del patrón Command.

    Encapsula la solicitud de registrar una toma de medicamento
    y delega la ejecución real al receiver (`TomaService`).
    """

    def __init__(
        self,
        receiver,
        paciente_id,
        medicamento_id,
        recordatorio_id,
        fecha_programada,
        fecha_hora_toma,
        estado="tomada",
        observaciones=None
    ):
        self.receiver = receiver
        self.paciente_id = paciente_id
        self.medicamento_id = medicamento_id
        self.recordatorio_id = recordatorio_id
        self.fecha_programada = fecha_programada
        self.fecha_hora_toma = fecha_hora_toma
        self.estado = estado
        self.observaciones = observaciones

    def execute(self):
        """
        Ejecuta el comando delegando en el receiver.
        """
        return self.receiver.registrar_toma(
            paciente_id=self.paciente_id,
            medicamento_id=self.medicamento_id,
            recordatorio_id=self.recordatorio_id,
            fecha_programada=self.fecha_programada,
            fecha_hora_toma=self.fecha_hora_toma,
            estado=self.estado,
            observaciones=self.observaciones
        )
