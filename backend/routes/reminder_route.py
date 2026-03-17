#############################################################################
#
#	Ruta para los recordatorios
#	prefix="/recordatorios" Hace que todas las rutas de este archivo, 
#				cuando existan empiecen con /recordatorios.
#	tags=["Recordatorios"]  Sirve para que Swagger /docs agrupe esas rutas
#				bajo el nombre de "Recordatorios"
#
#############################################################################

from fastapi import APIRouter # Importar la herramienta de FastAPI para agrupar rutas

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"]) # Crea el router de este módulo
