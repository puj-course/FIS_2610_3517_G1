from fastapi import APIRouter, HTTPException
from backend.services.resumen_paciente_service import ResumenPacienteService

router = APIRouter(prefix="/resumen", tags=["Resumen Paciente"])

service = ResumenPacienteService()


@router.get(
    "/{paciente_id}",
    responses={
        404: {"description": "Paciente no encontrado"},
        500: {"description": "Error interno al construir el resumen del paciente"},
    },
)
def obtener_resumen(paciente_id: int):
    try:
        resumen = service.construir_resumen(paciente_id)

    except LookupError:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    paciente = resumen.get("paciente", {})
    medicamentos = resumen.get("medicamentos_activos", [])
    historial = resumen.get("historial", [])
    cumplimiento = resumen.get("cumplimiento", {})

    total_tomas = cumplimiento.get("total_tomas", 0)
    tomas_realizadas = cumplimiento.get("tomas_realizadas", 0)
    porcentaje = cumplimiento.get("porcentaje", 0)

    tomas_a_tiempo = sum(
        1 for toma in historial
        if toma.get("estado") in ["a_tiempo", "tomado", "tomada"]
    )

    tomas_tarde = sum(
        1 for toma in historial
        if toma.get("estado") == "tarde"
    )

    tomas_omitidas = sum(
        1 for toma in historial
        if toma.get("estado") == "omitida"
    )

    tomas_pendientes = sum(
        1 for toma in historial
        if toma.get("estado") == "pendiente"
    )

    return {
        "paciente_id": paciente_id,
        "nombre_paciente": f"{paciente.get('nombres', '')} {paciente.get('apellidos', '')}".strip(),

        "total_medicamentos_activos": len(medicamentos),

        "total_tomas_esperadas": total_tomas,
        "total_tomas_esperadas_hoy": total_tomas,

        "tomas_realizadas": tomas_realizadas,
        "tomas_registradas_hoy": tomas_realizadas,

        "tomas_a_tiempo": tomas_a_tiempo,
        "tomas_tarde": tomas_tarde,
        "tomas_omitidas": tomas_omitidas,
        "tomas_pendientes": tomas_pendientes,

        "tomas_atrasadas": tomas_pendientes + tomas_omitidas,

        "porcentaje_cumplimiento": porcentaje,
        "alertas_activas": resumen.get("alertas", []),
        "historial": historial
    }
