from abc import ABC, abstractmethod


class Historial(ABC):
    # interfaz base que define lo de cualquier historial de tomas
    @abstractmethod
    def obtener_datos(self) -> dict:
        # esto devuelve un diccionario con los datos del historial de tomas
        pass


class HistorialTomas(Historial):
    # implementación concreta del historial de tomas
    def __init__(self, tomas: list):
        self._tomas = tomas

    def obtener_datos(self) -> dict:
        return {"historial": self._tomas}


class HistorialDecorator(Historial):
    # decorador base
    def __init__(self, historial: Historial):
        self._historial = historial

    def obtener_datos(self) -> dict:
        return self._historial.obtener_datos()


class CumplimientoDecorator(HistorialDecorator):
    # agrega cálculo de cumplimiento
    def obtener_datos(self) -> dict:
        datos = self._historial.obtener_datos()
        tomas = datos.get("historial", [])

        total = len(tomas)
        tomadas = sum(
            1 for toma in tomas
            if toma.get("estado") in ["tomado", "a_tiempo", "tarde"]
        )
        porcentaje = round((tomadas / total) * 100, 1) if total > 0 else 0

        datos["cumplimiento"] = {
            "total_tomas": total,
            "tomas_realizadas": tomadas,
            "porcentaje": porcentaje
        }
        return datos


class AlertasDecorator(HistorialDecorator):
    # agrega alertas para tomas no realizadas o atrasadas
    def obtener_datos(self) -> dict:
        datos = self._historial.obtener_datos()
        tomas = datos.get("historial", [])

        alertas = [
            {
                "medicamento": t.get("medicamento_nombre"),
                "fecha": t.get("fecha"),
                "hora_programada": t.get("hora_programada"),
                "mensaje": f"Toma de {t.get('medicamento_nombre')} no registrada el {t.get('fecha')}"
            }
            for t in tomas
            if t.get("estado") in ["omitida", "atrasado", "pendiente"]
        ]

        datos["alertas"] = alertas
        return datos