from fastapi import APIRouter, HTTPException
from backend.services.resumen_paciente_service import ResumenPacienteService

router = APIRouter(prefix="/resumen", tags=["Resumen Paciente"])

service = ResumenPacienteService()


@router.get("/{paciente_id}")
def obtener_resumen(paciente_id: int):
    try:
        return service.construir_resumen(paciente_id)

    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al construir el resumen del paciente: {str(e)}"
        )