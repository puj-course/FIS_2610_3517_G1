from backend.models import get_connection


class TomaRepository:
    """
    Patrón Repository para el acceso a la tabla de tomas.
    Centraliza todas las operaciones de la base de datos relacionadas con las tomas,
    desacoplando la lógica de negocio del acceso directo a la BD.
    """

    def registrar_toma(
        self,
        medicamento_id,
        paciente_id,
        fecha,
        hora_programada,
        hora_tomada=None,
        estado='pendiente',
        observaciones=None
    ):
        """
        Registra una nueva toma en la base de datos.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tomas (
                medicamento_id,
                paciente_id,
                fecha,
                hora_programada,
                hora_tomada,
                estado,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            medicamento_id,
            paciente_id,
            fecha,
            hora_programada,
            hora_tomada,
            estado,
            observaciones
        ))
        conn.commit()
        toma_id = cursor.lastrowid
        conn.close()
        return toma_id

    def obtener_tomas_del_dia(self, paciente_id, fecha):
        """
        Retorna todas las tomas del día de un paciente específico.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tomas
            WHERE paciente_id = ? AND fecha = ?
        """, (paciente_id, fecha))
        tomas = cursor.fetchall()
        conn.close()
        return tomas