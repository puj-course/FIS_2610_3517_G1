from abc import ABC, abstractmethod 
class Historial(ABC):
    #interfaz base que define lo de cualquier historial de tomas
    #uso patron decorator porque se pueden agregar funcionalidades a los historiales de tomas sin modificar su estructura base
    @abstractmethod
    def obtener_datos(self)->dict:
        #esto me devuelve un diccionario con los datos del historial de tomas, como fecha, hora, medicamento, dosis, etc
        pass
class HistorialTomas(Historial):
    #esto es ya como la implementacion concreta del historial de tomas, que puede ser decorada con otras funcionalidades
    #recibe las tomas crudas del endpoint y las las expone
    def __init__(self, tomas:list):
        self._tomas = tomas
    def obtener_datos(self)->dict:
        return {"historial": self._tomas}

class HistorialDecorator(Historial):
    #esto es el decorador base, que recibe un historial de tomas y lo decora con funcionalidades adicionales
    #es como si envolviera el objeto de Historial y delega obtener_datos al componente interno. 
    #y asi las subclases concretas pueden agregar funcionalidades adicionales a obtener_datos sin modificar la estructura base del historial de tomas
    def __init__(self, historial:Historial):
        self._historial = historial
    def obtener_datos(self)->dict:
        return self._historial.obtener_datos()
    
class CumplimientoDecorator(HistorialDecorator):
    #esto es un decorador concreto que agrega la funcionalidad de calcular el cumplimiento de las tomas en porcentaje para las tomas que se han cumplido respecto a las programadas
    def obtener_datos(self)->dict:
        datos=self._historial.obtener_datos()
        tomas=datos.get("historial",[])

        total=len(tomas)
      tomadas = sum(1 for toma in tomas if toma.get("estado") in ["a_tiempo", "tarde"])
        porcentaje=round((tomadas/total)*100,1)if total>0 else 0
        datos["cumplimiento"] = {
            "total_tomas": total,
            "tomas_realizadas": tomadas,
            "porcentaje": porcentaje
        }
        return datos

class AlertasDecorator(HistorialDecorator):
   #este es un decorador conreto que agrega la funcionalidad de generar alertas para las tomas atrasadas
    def obtener_datos(self) -> dict:
        datos = self._historial.obtener_datos()
        tomas = datos.get("historial", [])

        alertas = [
            {
                "medicamento": t.get("medicamento"),
                "fecha": t.get("fecha"),
                "hora_programada": t.get("hora_programada"),
                "mensaje": f"Toma de {t.get('medicamento')} no registrada el {t.get('fecha')}"
            }
            for t in tomas if t.get("estado") == "omitida"
        ]

        datos["alertas"] = alertas
        return datos
