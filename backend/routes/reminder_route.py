from datetime import date as date_type, datetime
from typing import Annotated, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.errors import PyMongoError

from backend.auth import verify_jwt
from backend.database import (
    medicamentos_col,
    pacientes_col,
    recordatorios_col,
    tomas_col,
)
from backend.validaciones import validar_recordatorio


try:
    from backend.alertas.bootstrap import publisher
except ImportError:
    publisher = None


router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])
security = HTTPBearer()

FORMATO_FECHA = "%m/%d/%Y"
ESTADOS_TOMADO = {"tomada", "a_tiempo", "tarde"}

RESPUESTA_400 = {"description": "Solicitud inválida"}
RESPUESTA_401 = {"description": "Token inválido o ausente"}
RESPUESTA_404 = {"description": "Recurso no encontrado"}
RESPUESTA_500 = {"description": "Error interno del servidor"}

RESPONSES_CREAR_RECORDATORIO = {
    400: RESPUESTA_400,
    404: RESPUESTA_404,
    500: RESPUESTA_500,
}

RESPONSES_AUTENTICADO = {
    401: RESPUESTA_401,
}

RESPONSES_MARCAR_TOMADO = {
    400: RESPUESTA_400,
    404: RESPUESTA_404,
}


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = verify_jwt(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    return payload


def serializar_recordatorio(
    recordatorio: dict,
    medicamento: Optional[dict] = None,
) -> dict:
    return {
        "id": str(recordatorio.get("_id")),
        "medicamento_id": recordatorio.get("medicamento_id"),
        "paciente_id": recordatorio.get("paciente_id"),
        "medicamento_nombre": (
            medicamento.get("nombre", "")
            if medicamento
            else recordatorio.get("medicamento_nombre", "")
        ),
        "dosis": (
            medicamento.get("dosis", "")
            if medicamento
            else recordatorio.get("dosis", "")
        ),
        "hora_recordatorio": recordatorio.get("hora_recordatorio", ""),
        "fecha_inicio": recordatorio.get("fecha_inicio", ""),
        "activo": recordatorio.get("activo", 1),
        "observaciones": recordatorio.get("observaciones", ""),
        "tomado": recordatorio.get("tomado", False),
    }


def obtener_medicamento_por_id(medicamento_id: str):
    try:
        return medicamentos_col.find_one({"_id": ObjectId(medicamento_id)})
    except InvalidId:
        return None


def _validar_datos_recordatorio(data: dict) -> None:
    errores = validar_recordatorio(data)

    if errores:
        raise HTTPException(status_code=400, detail="; ".join(errores))


def _obtener_medicamento_requerido(medicamento_id: str) -> dict:
    medicamento = obtener_medicamento_por_id(medicamento_id)

    if not medicamento:
        raise HTTPException(status_code=404, detail="El medicamento no existe")

    return medicamento


def _obtener_paciente_id_medicamento(medicamento: dict) -> str:
    paciente_id = medicamento.get("paciente_id")

    if not paciente_id:
        raise HTTPException(
            status_code=400,
            detail="El medicamento no tiene paciente asociado",
        )

    return paciente_id


def _construir_documento_recordatorio(data: dict, paciente_id: str) -> dict:
    return {
        "medicamento_id": str(data["medicamento_id"]).strip(),
        "paciente_id": paciente_id,
        "hora_recordatorio": data["hora_recordatorio"].strip(),
        "fecha_inicio": data["fecha_inicio"].strip(),
        "activo": int(data.get("activo", 1)),
        "observaciones": data.get("observaciones", "").strip(),
        "tomado": False,
    }


def _notificar_recordatorio_creado(recordatorio_id: str, recordatorio: dict) -> None:
    if not publisher:
        return

    try:
        publisher.notify({
            "type": "reminder_created",
            "recordatorio_id": recordatorio_id,
            "medicamento_id": recordatorio["medicamento_id"],
            "paciente_id": recordatorio["paciente_id"],
            "hora_recordatorio": recordatorio["hora_recordatorio"],
            "fecha_inicio": recordatorio["fecha_inicio"],
            "activo": recordatorio["activo"],
            "observaciones": recordatorio["observaciones"],
        })
    except (AttributeError, RuntimeError, TypeError):
        return


def _parsear_fecha(fecha: str):
    try:
        return datetime.strptime(fecha, FORMATO_FECHA).date()
    except ValueError:
        return None


def _fecha_inicio_valida(fecha_inicio: str, hoy: date_type) -> bool:
    inicio = _parsear_fecha(fecha_inicio)
    return inicio is not None and inicio <= hoy


def _fecha_fin_vigente(fecha_fin: str, hoy: date_type) -> bool:
    if not fecha_fin:
        return True

    fin = _parsear_fecha(fecha_fin)
    return fin is None or fin >= hoy


def _medicamento_vigente_hoy(medicamento: dict, hoy: date_type) -> bool:
    return (
        _fecha_inicio_valida(medicamento.get("fecha_inicio", ""), hoy)
        and _fecha_fin_vigente(medicamento.get("fecha_fin", ""), hoy)
    )


def _obtener_horarios(medicamento: dict) -> list[str]:
    return [
        hora.strip()
        for hora in medicamento.get("horario", "").split(",")
        if hora.strip()
    ]


def _buscar_toma(medicamento_id: str, hoy_iso: str, hora: str):
    toma = tomas_col.find_one({
        "medicamento_id": medicamento_id,
        "estado": {"$in": list(ESTADOS_TOMADO)}
    })
    if toma:
        return toma
    try:
        toma = tomas_col.find_one({
            "medicamento_id": ObjectId(medicamento_id),
            "estado": {"$in": list(ESTADOS_TOMADO)}
        })
    except Exception:
        pass
    return toma


def _esta_tomado(toma: Optional[dict]) -> bool:
    return toma is not None and toma.get("estado") in ESTADOS_TOMADO


def _construir_item_panel_completo(
    medicamento: dict,
    hora: str,
    hoy_iso: str,
) -> dict:
    medicamento_id = str(medicamento["_id"])
    toma = _buscar_toma(medicamento_id, hoy_iso, hora)

    return {
        "medicamento_id": medicamento_id,
        "medicamento": medicamento.get("nombre", ""),
        "dosis": medicamento.get("dosis", ""),
        "hora": hora,
        "tomado": _esta_tomado(toma),
    }


def _construir_items_medicamento(
    medicamento: dict,
    hoy: date_type,
    hoy_iso: str,
) -> list[dict]:
    if not _medicamento_vigente_hoy(medicamento, hoy):
        return []

    return [
        _construir_item_panel_completo(medicamento, hora, hoy_iso)
        for hora in _obtener_horarios(medicamento)
    ]


def _obtener_medicamentos_paciente(paciente_id: str) -> list[dict]:
    return list(medicamentos_col.find({"paciente_id": paciente_id}))


def _construir_panel_completo_paciente(
    paciente: dict,
    hoy: date_type,
    hoy_iso: str,
) -> Optional[dict]:
    paciente_id = str(paciente["_id"])
    medicamentos = _obtener_medicamentos_paciente(paciente_id)

    items = [
        item
        for medicamento in medicamentos
        for item in _construir_items_medicamento(medicamento, hoy, hoy_iso)
    ]

    if not items:
        return None

    return {
        "paciente_id": paciente_id,
        "nombres": paciente.get("nombres", ""),
        "apellidos": paciente.get("apellidos", ""),
        "medicamentos": items,
    }


def _obtener_pacientes_cuidador(cuidador_id: str) -> list[dict]:
    return list(pacientes_col.find({"cuidador_id": cuidador_id}))


def _construir_item_panel_dia(recordatorio: dict) -> dict:
    medicamento = obtener_medicamento_por_id(recordatorio.get("medicamento_id"))

    return {
        "recordatorio_id": str(recordatorio["_id"]),
        "medicamento_id": recordatorio.get("medicamento_id"),
        "medicamento": medicamento.get("nombre", "") if medicamento else "",
        "dosis": medicamento.get("dosis", "") if medicamento else "",
        "hora": recordatorio.get("hora_recordatorio", ""),
        "tomado": recordatorio.get("tomado", False),
    }


def _obtener_recordatorios_activos_paciente(
    paciente_id: str,
    hoy: str,
) -> list[dict]:
    return list(recordatorios_col.find({
        "paciente_id": paciente_id,
        "activo": 1,
        "fecha_inicio": {"$lte": hoy},
    }))


def _construir_panel_dia_paciente(
    paciente: dict,
    hoy: str,
) -> Optional[dict]:
    paciente_id = str(paciente["_id"])
    recordatorios = _obtener_recordatorios_activos_paciente(paciente_id, hoy)
    medicamentos = [_construir_item_panel_dia(r) for r in recordatorios]

    if not medicamentos:
        return None

    return {
        "paciente_id": paciente_id,
        "nombres": paciente.get("nombres", ""),
        "apellidos": paciente.get("apellidos", ""),
        "medicamentos": medicamentos,
    }


def _serializar_recordatorio_panel_paciente(
    recordatorio: dict,
    paciente_id: str,
) -> dict:
    medicamento = obtener_medicamento_por_id(recordatorio.get("medicamento_id"))

    return {
        "recordatorio_id": str(recordatorio["_id"]),
        "paciente_id": paciente_id,
        "medicamento_id": recordatorio.get("medicamento_id"),
        "medicamento_nombre": medicamento.get("nombre", "") if medicamento else "",
        "dosis": medicamento.get("dosis", "") if medicamento else "",
        "hora_recordatorio": recordatorio.get("hora_recordatorio", ""),
        "fecha_inicio": recordatorio.get("fecha_inicio", ""),
        "tomado": recordatorio.get("tomado", False),
        "observaciones": recordatorio.get("observaciones", ""),
    }


@router.post("/", responses=RESPONSES_CREAR_RECORDATORIO)
def crear_recordatorio(data: dict):
    _validar_datos_recordatorio(data)

    medicamento_id = str(data["medicamento_id"]).strip()
    medicamento = _obtener_medicamento_requerido(medicamento_id)
    paciente_id = _obtener_paciente_id_medicamento(medicamento)
    nuevo_recordatorio = _construir_documento_recordatorio(data, paciente_id)

    try:
        resultado = recordatorios_col.insert_one(nuevo_recordatorio)
    except PyMongoError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el recordatorio: {str(exc)}",
        ) from exc

    recordatorio_id = str(resultado.inserted_id)
    _notificar_recordatorio_creado(recordatorio_id, nuevo_recordatorio)

    return {
        "mensaje": "Recordatorio creado correctamente",
        "recordatorio_id": recordatorio_id,
    }


@router.get("/panel-completo", responses=RESPONSES_AUTENTICADO)
def obtener_panel_completo(
    usuario: Annotated[dict, Depends(obtener_usuario_actual)],
):
    hoy = date_type.today()
    hoy_iso = hoy.isoformat()
    cuidador_id = usuario.get("id")

    pacientes = _obtener_pacientes_cuidador(cuidador_id)

    panel = [
        panel_paciente
        for paciente in pacientes
        if (
            panel_paciente := _construir_panel_completo_paciente(
                paciente,
                hoy,
                hoy_iso,
            )
        )
    ]

    return {"panel": panel}


@router.get("/panel-dia", responses=RESPONSES_AUTENTICADO)
def obtener_panel_dia(
    usuario: Annotated[dict, Depends(obtener_usuario_actual)],
):
    hoy = date_type.today().strftime(FORMATO_FECHA)
    cuidador_id = usuario.get("id")
    pacientes = _obtener_pacientes_cuidador(cuidador_id)

    panel = [
        panel_paciente
        for paciente in pacientes
        if (
            panel_paciente := _construir_panel_dia_paciente(
                paciente,
                hoy,
            )
        )
    ]

    return {"panel": panel}


@router.get("/panel-dia/{paciente_id}", responses=RESPONSES_AUTENTICADO)
def obtener_panel_dia_paciente(
    paciente_id: str,
    usuario: Annotated[dict, Depends(obtener_usuario_actual)],
):
    recordatorios = list(recordatorios_col.find({
        "paciente_id": paciente_id,
        "activo": 1,
    }))

    resultado = [
        _serializar_recordatorio_panel_paciente(recordatorio, paciente_id)
        for recordatorio in recordatorios
    ]

    return {"recordatorios": resultado}


@router.get("/retrasados/{paciente_id}")
def listar_recordatorios_retrasados(paciente_id: str):
    recordatorios = list(recordatorios_col.find({
        "paciente_id": paciente_id,
        "activo": 1,
        "tomado": False,
    }))

    resultado = [
        serializar_recordatorio(r, obtener_medicamento_por_id(r.get("medicamento_id")))
        for r in recordatorios
    ]

    return {"recordatorios_retrasados": resultado}


@router.get("/{paciente_id}")
def listar_recordatorios(paciente_id: str):
    recordatorios = list(recordatorios_col.find({"paciente_id": paciente_id}))

    resultado = [
        serializar_recordatorio(r, obtener_medicamento_por_id(r.get("medicamento_id")))
        for r in recordatorios
    ]

    return {"recordatorios": resultado}


@router.patch(
    "/{recordatorio_id}/tomado",
    responses=RESPONSES_MARCAR_TOMADO,
)
def marcar_recordatorio_como_tomado(recordatorio_id: str):
    try:
        filtro = {"_id": ObjectId(recordatorio_id)}
    except InvalidId as exc:
        raise HTTPException(
            status_code=400,
            detail="ID de recordatorio inválido",
        ) from exc

    resultado = recordatorios_col.update_one(filtro, {"$set": {"tomado": True}})

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Recordatorio no encontrado",
        )

    return {
        "mensaje": "Recordatorio marcado como tomado correctamente",
        "recordatorio_id": recordatorio_id,
    }