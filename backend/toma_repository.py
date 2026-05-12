from backend.database import tomas_col


class TomaRepository:
    """
    Patrón Repository para el acceso a la colección de tomas en MongoDB.
    Centraliza las operaciones de base de datos relacionadas con las tomas.
    """

    def registrar_toma(
        self,
        medicamento_id,
        paciente_id,
        fecha,
        hora_programada,
        hora_tomada=None,
        estado="pendiente",
        observaciones=None
    ):
        documento = {
            "medicamento_id": str(medicamento_id),
            "paciente_id": str(paciente_id),
            "fecha": fecha,
            "hora_programada": hora_programada,
            "hora_tomada": hora_tomada,
            "estado": estado,
            "observaciones": observaciones
        }

        resultado = tomas_col.insert_one(documento)

        return str(resultado.inserted_id)

    def obtener_tomas_del_dia(self, paciente_id, fecha):
        tomas = list(
            tomas_col.find({
                "paciente_id": str(paciente_id),
                "fecha": fecha
            }).sort("hora_programada", 1)
        )

        resultado = []

        for t in tomas:
            resultado.append({
                "id": str(t.get("_id")),
                "medicamento_id": t.get("medicamento_id"),
                "paciente_id": t.get("paciente_id"),
                "fecha": t.get("fecha"),
                "hora_programada": t.get("hora_programada"),
                "hora_tomada": t.get("hora_tomada"),
                "estado": t.get("estado"),
                "observaciones": t.get("observaciones")
            })

        return resultado