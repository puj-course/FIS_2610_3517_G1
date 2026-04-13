######################################################################################
#	toma_service es el fichero que actuara como el Receiver del patron Command
#	Es decir que es el que realmente sabe como realizar una toma.
#
#########################################################################################
import sqlite3
from typing import Any, Dict, Optional

from backend.models import DB_PATH
try:
    from backend.alertas.bootstrap import publisher
except Exception:
    publisher = None

class TomaService:
    """
    Receiver del patrón Command.

    Esta clase contiene la lógica real de negocio para registrar
    una toma de medicamento en la tabla `tomas_medicamento`.
    """

    def registrar_toma(
        self,
        paciente_id: int,
        medicamento_id: int,
        recordatorio_id: int,
        fecha_programada: str,
        fecha_hora_toma: str,
        estado: str = "tomada",
        observaciones: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra una toma de medicamento en la base de datos.

        Parámetros:
            paciente_id: ID del paciente
            medicamento_id: ID del medicamento
            recordatorio_id: ID del recordatorio asociado
            fecha_programada: fecha/hora programada de la toma
            fecha_hora_toma: fecha/hora real en que se tomó
            estado: estado de la toma (por defecto: 'tomada')
            observaciones: texto opcional

        Retorna:
            dict con resultado de la operación

        Lanza:
            ValueError: si faltan datos o hay inconsistencia en relaciones
            LookupError: si paciente, medicamento o recordatorio no existen
            FileExistsError: si ya existe una toma para ese recordatorio y fecha
            RuntimeError: si ocurre un error inesperado en base de datos
        """

        self._validar_campos_obligatorios(
            paciente_id=paciente_id,
            medicamento_id=medicamento_id,
            recordatorio_id=recordatorio_id,
            fecha_programada=fecha_programada,
            fecha_hora_toma=fecha_hora_toma,
            estado=estado
        )

        conn = None

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # 1. Validar paciente existente
            paciente = self._obtener_paciente(cur, paciente_id)

            if not paciente:
                raise LookupError("El paciente no existe")

            # 2. Validar medicamento existente
            medicamento = self._obtener_medicamento(cur, medicamento_id)

            if not medicamento:
                raise LookupError("El medicamento no existe")

            # 3. Validar que el medicamento pertenezca al paciente
            if medicamento["paciente_id"] != paciente_id:
                raise ValueError("El medicamento no pertenece al paciente")

            # 4. Validar recordatorio existente
            recordatorio = self._obtener_recordatorio(cur, recordatorio_id)

            if not recordatorio:
                raise LookupError("El recordatorio no existe")

            # 5. Validar que el recordatorio pertenezca al medicamento
            if recordatorio["medicamento_id"] != medicamento_id:
                raise ValueError("El recordatorio no pertenece al medicamento")

            # 6. Validar duplicado por UNIQUE(recordatorio_id, fecha_programada)
            duplicado = self._obtener_toma_duplicada(
                cur,
                recordatorio_id=recordatorio_id,
                fecha_programada=fecha_programada
            )

            if duplicado:
                raise FileExistsError(
                    "Ya existe una toma registrada para ese recordatorio y fecha programada"
                )

            # 7. Insertar la toma
            cur.execute(
                """
                INSERT INTO tomas_medicamento (
                    paciente_id,
                    medicamento_id,
                    recordatorio_id,
                    fecha_programada,
                    fecha_hora_toma,
                    estado,
                    observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    paciente_id,
                    medicamento_id,
                    recordatorio_id,
                    fecha_programada,
                    fecha_hora_toma,
                    estado,
                    observaciones
                )
            )

            conn.commit()
            toma_id = cur.lastrowid

            if publisher:
                publisher.notify({
                    "type": "medication_taken",
                    "toma_id": toma_id,
                    "paciente_id": paciente_id,
                    "medicamento_id": medicamento_id,
                    "recordatorio_id": recordatorio_id,
                    "fecha_programada": fecha_programada,
                    "fecha_hora_toma": fecha_hora_toma,
                    "estado": estado,
                    "observaciones": observaciones
                })

            return {
                "ok": True,
                "mensaje": "Toma registrada correctamente",
                "toma_id": toma_id,
                "data": {
                    "paciente_id": paciente_id,
                    "medicamento_id": medicamento_id,
                    "recordatorio_id": recordatorio_id,
                    "fecha_programada": fecha_programada,
                    "fecha_hora_toma": fecha_hora_toma,
                    "estado": estado,
                    "observaciones": observaciones
                }
            }

        except sqlite3.IntegrityError as e:
            # Refuerzo por si la BD dispara la restricción UNIQUE
            raise FileExistsError(
                "Conflicto de integridad al registrar la toma"
            ) from e

        except (ValueError, LookupError, FileExistsError):
            # Re-lanzamos errores de negocio tal cual
            raise

        except sqlite3.Error as e:
            raise RuntimeError(
                f"Error de base de datos al registrar la toma: {str(e)}"
            ) from e

        finally:
            if conn is not None:
                conn.close()

    def _validar_campos_obligatorios(
        self,
        paciente_id: int,
        medicamento_id: int,
        recordatorio_id: int,
        fecha_programada: str,
        fecha_hora_toma: str,
        estado: str
    ) -> None:
        """
        Valida que todos los campos requeridos estén presentes.
        """
        if not paciente_id:
            raise ValueError("El paciente_id es obligatorio")

        if not medicamento_id:
            raise ValueError("El medicamento_id es obligatorio")

        if not recordatorio_id:
            raise ValueError("El recordatorio_id es obligatorio")

        if not fecha_programada or not str(fecha_programada).strip():
            raise ValueError("La fecha_programada es obligatoria")

        if not fecha_hora_toma or not str(fecha_hora_toma).strip():
            raise ValueError("La fecha_hora_toma es obligatoria")

        if not estado or not str(estado).strip():
            raise ValueError("El estado es obligatorio")

    def _obtener_paciente(self, cur: sqlite3.Cursor, paciente_id: int) -> Optional[sqlite3.Row]:
        """
        Consulta un paciente por ID.
        """
        cur.execute(
            "SELECT id FROM pacientes WHERE id = ?",
            (paciente_id,)
        )
        return cur.fetchone()

    def _obtener_medicamento(self, cur: sqlite3.Cursor, medicamento_id: int) -> Optional[sqlite3.Row]:
        """
        Consulta un medicamento por ID.
        """
        cur.execute(
            """
            SELECT id, paciente_id
            FROM medicamentos
            WHERE id = ?
            """,
            (medicamento_id,)
        )
        return cur.fetchone()

    def _obtener_recordatorio(self, cur: sqlite3.Cursor, recordatorio_id: int) -> Optional[sqlite3.Row]:
        """
        Consulta un recordatorio por ID.
        """
        cur.execute(
            """
            SELECT id, medicamento_id
            FROM recordatorios
            WHERE id = ?
            """,
            (recordatorio_id,)
        )
        return cur.fetchone()

    def _obtener_toma_duplicada(
        self,
        cur: sqlite3.Cursor,
        recordatorio_id: int,
        fecha_programada: str
    ) -> Optional[sqlite3.Row]:
        """
        Busca si ya existe una toma para la combinación
        (recordatorio_id, fecha_programada).
        """
        cur.execute(
            """
            SELECT id
            FROM tomas_medicamento
            WHERE recordatorio_id = ? AND fecha_programada = ?
            """,
            (recordatorio_id, fecha_programada)
        )
        return cur.fetchone() 