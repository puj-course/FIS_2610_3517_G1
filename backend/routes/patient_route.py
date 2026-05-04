# patient_route.py
# Migrado de SQLite a MongoDB
# Los pacientes se asocian al cuidador que los registró mediante cuidador_id

from fastapi import APIRouter, HTTPException, status, Header
from backend.database import pacientes_col, tomas_col
from backend.validaciones import validar_paciente
from backend.factories.paciente_factory import PacienteGeneralFactory
from backend.auth import verify_jwt
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

def obtener_cuidador_id(authorization: str) -> str:
    # Extrae el id del cuidador desde el token JWT del header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado"
        )
    token = authorization.replace("Bearer ", "")
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return payload["id"]


@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def registrar_paciente(data: dict, authorization: str = Header(None)):

    # Validamos los datos del formulario
    errores = validar_paciente(data)
    if errores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errores
        )

    # Obtenemos el id del cuidador desde el token
    cuidador_id = obtener_cuidador_id(authorization)

    # Verificamos duplicado por tipo y número de documento del mismo cuidador
    existente = pacientes_col.find_one({
        "tipo_documento": data["tipo_documento"],
        "numero_documento": data["numero_documento"],
        "cuidador_id": cuidador_id
    })
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un paciente con ese documento"
        )

    # Usamos la fábrica para construir el objeto paciente
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(data)

    # Convertimos a diccionario y agregamos el cuidador_id
    doc = paciente.como_dict()
    doc["cuidador_id"] = cuidador_id

    # Insertamos en MongoDB
    resultado = pacientes_col.insert_one(doc)

    return {
        "message": "Paciente registrado exitosamente",
        "paciente_id": str(resultado.inserted_id)
    }


@router.get("/pacientes")
def obtener_pacientes(authorization: str = Header(None)):

    # Solo mostramos los pacientes del cuidador autenticado
    cuidador_id = obtener_cuidador_id(authorization)
    pacientes = list(pacientes_col.find({"cuidador_id": cuidador_id}))

    resultado = []
    for p in pacientes:
        paciente_id = str(p["_id"])

        # Consultamos tomas atrasadas y omitidas del paciente en MongoDB
        total_tomas_atrasadas = tomas_col.count_documents({
            "paciente_id": paciente_id,
            "estado": "atrasada"
        })
        total_tomas_omitidas = tomas_col.count_documents({
            "paciente_id": paciente_id,
            "estado": "omitida"
        })

        tiene_tomas_atrasadas = total_tomas_atrasadas > 0
        tiene_tomas_omitidas = total_tomas_omitidas > 0

        # Determinamos el tipo de alerta
        if tiene_tomas_atrasadas and tiene_tomas_omitidas:
            alerta_tomas = "mixta"
        elif tiene_tomas_atrasadas:
            alerta_tomas = "atrasada"
        elif tiene_tomas_omitidas:
            alerta_tomas = "omitida"
        else:
            alerta_tomas = None

        resultado.append({
            "id": paciente_id,
            "nombres": p.get("nombres", ""),
            "apellidos": p.get("apellidos", ""),
            "fecha_nacimiento": p.get("fecha_nacimiento", ""),
            "genero": p.get("genero", ""),
            "tipo_documento": p.get("tipo_documento", ""),
            "numero_documento": p.get("numero_documento", ""),
            "telefono_contacto": p.get("telefono_contacto", ""),
            "eps_aseguradora": p.get("eps_aseguradora", ""),
            "diagnostico_principal": p.get("diagnostico_principal", ""),
            "alergias_conocidas": p.get("alergias_conocidas", ""),
            "observaciones_adicionales": p.get("observaciones_adicionales", ""),
            "tiene_tomas_atrasadas": tiene_tomas_atrasadas,
            "tiene_tomas_omitidas": tiene_tomas_omitidas,
            "total_tomas_atrasadas": total_tomas_atrasadas,
            "total_tomas_omitidas": total_tomas_omitidas,
            "alerta_tomas": alerta_tomas,
            "alerta": {
                "tiene_alerta": tiene_tomas_atrasadas or tiene_tomas_omitidas,
                "tipo": alerta_tomas if alerta_tomas else "sin_alerta",
                "atrasadas": total_tomas_atrasadas,
                "omitidas": total_tomas_omitidas,
                "total": total_tomas_atrasadas + total_tomas_omitidas
            }
        })

    return resultado


@router.get("/pacientes/{paciente_id}")
def obtener_paciente(paciente_id: str, authorization: str = Header(None)):

    cuidador_id = obtener_cuidador_id(authorization)

    # Buscamos el paciente verificando que pertenezca al cuidador
    try:
        p = pacientes_col.find_one({
            "_id": ObjectId(paciente_id),
            "cuidador_id": cuidador_id
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de paciente inválido"
        )

    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )

    return {
        "id": str(p["_id"]),
        "nombres": p.get("nombres", ""),
        "apellidos": p.get("apellidos", ""),
        "fecha_nacimiento": p.get("fecha_nacimiento", ""),
        "genero": p.get("genero", ""),
        "tipo_documento": p.get("tipo_documento", ""),
        "numero_documento": p.get("numero_documento", ""),
        "telefono_contacto": p.get("telefono_contacto", ""),
        "eps_aseguradora": p.get("eps_aseguradora", ""),
        "diagnostico_principal": p.get("diagnostico_principal", ""),
        "alergias_conocidas": p.get("alergias_conocidas", ""),
        "observaciones_adicionales": p.get("observaciones_adicionales", "")
    }