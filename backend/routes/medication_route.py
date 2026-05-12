from datetime import date as date_type, datetime
from typing import Annotated, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from backend.database import medicamentos_col, pacientes_col
from backend.routes.reminder_route import obtener_usuario_actual
from backend.validaciones import validar_medicamento


router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])

ESTADOS_TOMADO = {"tomada", "a_tiempo", "tarde"}
FORMATO_FECHA = "%m/%d/%Y"


def _obtener_paciente_por_id(paciente_id: str):
    try:
        return pacientes_col.find_one({"_id": ObjectId(paciente_id)})
    except InvalidId as exc:
        raise HTTPException(
            status_code=400,
            detail="ID de paciente inválido",
        ) from exc


def _validar_paciente_existe(paciente_id: str):
    paciente = _obtener_paciente_por_id(paciente_id)

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="El paciente no existe",
        )

    return paciente


def _normalizar_nombre_medicamento(data: dict) -> str:
    return data["nombre_medicamento"].strip().lower()


def _validar_medicamento_no_duplicado(paciente_id: str, nombre_medicamento: str):
    duplicado = medicamentos_col.find_one({
        "paciente_id": paciente_id,
        "nombre": nombre_medicamento,
    })

    if duplicado:
        raise HTTPException(
            status_code=400,
            detail="El paciente ya tiene registrado este medicamento",
        )


def _construir_observaciones(data: dict) -> str:
    observaciones_extra = (
        f'Concentración: {data["concentracion"]} | '
        f'Forma farmacéutica: {data["forma_farmaceutica"]}'
    )

    observaciones_usuario = data.get("observaciones", "").strip()

    if observaciones_usuario:
        return f"{observaciones_extra} | {observaciones_usuario}"

    return observaciones_extra


def _construir_documento_medicamento(data: dict, paciente_id: str) -> dict:
    return {
        "nombre": _normalizar_nombre_medicamento(data),
        "dosis": f'{data["dosis_cantidad"]} {data["dosis_unidad"]}',
        "frecuencia": data["frecuencia"].strip(),
        "horario": ", ".join(data["horarios"]),
        "fecha_inicio": data["fecha_inicio"].strip(),
        "fecha_fin": data.get("fecha_fin", "").strip(),
        "observaciones": _construir_observaciones(data),
        "paciente_id": paciente_id,
    }


def _serializar_medicamento(medicamento: dict) -> dict:
    return {
        "id": str(medicamento["_id"]),
        "nombre": medicamento.get("nombre", ""),
        "dosis": medicamento.get("dosis", ""),
        "frecuencia": medicamento.get("frecuencia", ""),
        "horario": medicamento.get("horario", ""),
        "fecha_inicio": medicamento.get("fecha_inicio", ""),
        "observaciones": medicamento.get("observaciones", ""),
        "paciente_id": medicamento.get("paciente_id", ""),
    }


def _fecha_fin_vencida(fecha_fin: str, hoy: date_type) -> bool:
    if not fecha_fin:
        return False

    try:
        fin = datetime.strptime(fecha_fin, FORMATO_FECHA).date()
    except ValueError:
        return False

    return fin < hoy


def _obtener_horarios(medicamento: dict) -> list[str]:
    return [
        hora.strip()
        for hora in medicamento.get("horario", "").split(",")
        if hora.strip()
    ]


def _buscar_toma_medicamento(
    tomas_col,
    medicamento_id: str,
    hoy_iso: str,
    hora: str,
) -> Optional[dict]:
    return tomas_col.find_one({
        "medicamento_id": medicamento_id,
        "fecha_programada": {"$regex": f"^{hoy_iso}.*{hora}"},
    })


def _toma_esta_registrada(toma: Optional[dict]) -> bool:
    return toma is not None and toma.get("estado") in ESTADOS_TOMADO


def _construir_item_medicamento(
    medicamento: dict,
    hora: str,
    tomado: bool,
) -> dict:
    return {
        "medicamento_id": str(medicamento["_id"]),
        "medicamento": medicamento.get("nombre", ""),
        "dosis": medicamento.get("dosis", ""),
        "hora": hora,
        "tomado": tomado,
    }


def _construir_items_medicamento(
    medicamento: dict,
    tomas_col,
    hoy_iso: str,
) -> list[dict]:
    medicamento_id = str(medicamento["_id"])
    items = []

    for hora in _obtener_horarios(medicamento):
        toma = _buscar_toma_medicamento(tomas_col, medicamento_id, hoy_iso, hora)
        items.append(
            _construir_item_medicamento(
                medicamento=medicamento,
                hora=hora,
                tomado=_toma_esta_registrada(toma),
            )
        )

    return items


def _construir_items_panel(
    medicamentos: list[dict],
    tomas_col,
    hoy_iso: str,
    hoy: date_type,
) -> list[dict]:
    items = []

    for medicamento in medicamentos:
        if _fecha_fin_vencida(medicamento.get("fecha_fin", ""), hoy):
            continue

        items.extend(
            _construir_items_medicamento(
                medicamento=medicamento,
                tomas_col=tomas_col,
                hoy_iso=hoy_iso,
            )
        )

    return items


def _obtener_medicamentos_activos_paciente(
    paciente_id: str,
    hoy_backend: str,
) -> list[dict]:
    return list(
        medicamentos_col.find({
            "paciente_id": paciente_id,
            "fecha_inicio": {"$lte": hoy_backend},
        })
    )


def _construir_panel_paciente(
    paciente: dict,
    tomas_col,
    hoy_backend: str,
    hoy_iso: str,
    hoy: date_type,
) -> Optional[dict]:
    paciente_id = str(paciente["_id"])
    medicamentos = _obtener_medicamentos_activos_paciente(
        paciente_id=paciente_id,
        hoy_backend=hoy_backend,
    )

    items = _construir_items_panel(
        medicamentos=medicamentos,
        tomas_col=tomas_col,
        hoy_iso=hoy_iso,
        hoy=hoy,
    )

    if not items:
        return None

    return {
        "paciente_id": paciente_id,
        "nombres": paciente.get("nombres", ""),
        "apellidos": paciente.get("apellidos", ""),
        "medicamentos": items,
    }


@router.post("/")
def registrar_medicamento(data: dict):
    errores = validar_medicamento(data)

    if errores:
        raise HTTPException(status_code=400, detail=errores)

    try:
        paciente_id = data["paciente_id"]
        _validar_paciente_existe(paciente_id)

        nombre_medicamento = _normalizar_nombre_medicamento(data)
        _validar_medicamento_no_duplicado(paciente_id, nombre_medicamento)

        nuevo_medicamento = _construir_documento_medicamento(data, paciente_id)
        resultado = medicamentos_col.insert_one(nuevo_medicamento)

        return {
            "mensaje": "Medicamento registrado exitosamente",
            "medicamento_id": str(resultado.inserted_id),
        }

    except HTTPException:
        raise

    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Datos inválidos para registrar medicamento: {str(exc)}",
        ) from exc


@router.get("/paciente/{paciente_id}")
def obtener_medicamentos_paciente(paciente_id: str):
    try:
        medicamentos = list(
            medicamentos_col.find(
                {"paciente_id": paciente_id}
            ).sort("nombre", 1)
        )

        return [
            _serializar_medicamento(medicamento)
            for medicamento in medicamentos
        ]

    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener medicamentos: {str(exc)}",
        ) from exc


@router.get("/panel-completo")
def obtener_panel_completo(
    usuario: Annotated[dict, Depends(obtener_usuario_actual)]
):
    from backend.database import tomas_col

    hoy = date_type.today()
    hoy_backend = hoy.strftime(FORMATO_FECHA)
    hoy_iso = hoy.isoformat()
    cuidador_id = usuario.get("id")

    pacientes = list(pacientes_col.find({"cuidador_id": cuidador_id}))

    panel = [
        panel_paciente
        for paciente in pacientes
        if (
            panel_paciente := _construir_panel_paciente(
                paciente=paciente,
                tomas_col=tomas_col,
                hoy_backend=hoy_backend,
                hoy_iso=hoy_iso,
                hoy=hoy,
            )
        )
    ]

    return {"panel": panel}