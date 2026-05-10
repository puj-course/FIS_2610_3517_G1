# validaciones.py
from datetime import datetime
from bson import ObjectId


TIPOS_DOCUMENTO = ["CC", "TI", "CE", "PA", "RC"]
GENEROS = ["Masculino", "Femenino", "Otro","no_especifica"]


def es_object_id_valido(valor) -> bool:
    return isinstance(valor, str) and ObjectId.is_valid(valor)


def validar_paciente(data: dict) -> list:
    errores = []

    campos_obligatorios = {
        "nombres": "El nombre es obligatorio",
        "apellidos": "Los apellidos son obligatorios",
        "fecha_nacimiento": "La fecha de nacimiento es obligatoria",
        "genero": "El género es obligatorio",
        "tipo_documento": "El tipo de documento es obligatorio",
        "numero_documento": "El número de documento es obligatorio",
        "telefono_contacto": "El teléfono de contacto es obligatorio",
        "eps_aseguradora": "La EPS/aseguradora es obligatoria",
        "diagnostico_principal": "El diagnóstico principal es obligatorio",
    }

    for campo, mensaje in campos_obligatorios.items():
        valor = data.get(campo, "")
        if not valor or str(valor).strip() == "":
            errores.append(mensaje)

    if errores:
        return errores

    try:
        fecha = datetime.strptime(data["fecha_nacimiento"], "%m/%d/%Y")
        if fecha > datetime.now():
            errores.append("La fecha de nacimiento no puede ser futura")
    except ValueError:
        errores.append("La fecha de nacimiento debe tener formato mm/dd/yyyy")

    if data["genero"] not in GENEROS:
        errores.append(f"El género debe ser uno de: {', '.join(GENEROS)}")

    if data["tipo_documento"] not in TIPOS_DOCUMENTO:
        errores.append(f"El tipo de documento debe ser uno de: {', '.join(TIPOS_DOCUMENTO)}")

    if not data["numero_documento"].isdigit():
        errores.append("El número de documento debe contener solo números")

    telefono = data["telefono_contacto"].strip()
    if not telefono.isdigit() or not (7 <= len(telefono) <= 10):
        errores.append("El teléfono debe contener solo números y tener entre 7 y 10 dígitos")

    return errores


def verificar_duplicado(numero_documento: str, tipo_documento: str, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM pacientes WHERE numero_documento = ? AND tipo_documento = ?",
        (numero_documento, tipo_documento)
    )
    resultado = cursor.fetchone()
    return resultado is not None


def validar_formato_medicamento(data: dict) -> list:
    errores = []

    nombre = str(data.get("nombre_medicamento", "")).strip()
    if nombre and len(nombre) < 2:
        errores.append("El nombre del medicamento debe tener al menos 2 caracteres")

    fecha = str(data.get("fecha_inicio", "")).strip()
    if fecha:
        try:
            datetime.strptime(fecha, "%m/%d/%Y")
        except ValueError:
            errores.append("La fecha de inicio debe tener formato mm/dd/yyyy")

    return errores


def validar_medicamento(data: dict) -> list:
    errores = []

    campos_obligatorios = {
        "nombre_medicamento": "El nombre del medicamento es obligatorio",
        "concentracion": "La concentración es obligatoria",
        "forma_farmaceutica": "La forma farmacéutica es obligatoria",
        "dosis_cantidad": "La dosis es obligatoria",
        "dosis_unidad": "La unidad de la dosis es obligatoria",
        "frecuencia": "La frecuencia es obligatoria",
        "fecha_inicio": "La fecha de inicio es obligatoria",
        "paciente_id": "El paciente_id es obligatorio"
    }

    for campo, mensaje in campos_obligatorios.items():
        valor = data.get(campo, "")
        if valor is None or str(valor).strip() == "":
            errores.append(mensaje)

    horarios = data.get("horarios", [])
    if not isinstance(horarios, list) or len(horarios) == 0:
        errores.append("Debe ingresar al menos un horario")

    if errores:
        return errores

    try:
        dosis_cantidad = float(data["dosis_cantidad"])
        if dosis_cantidad <= 0:
            errores.append("La dosis debe ser un número mayor que 0")
    except (ValueError, TypeError):
        errores.append("La dosis debe ser un número válido")

    paciente_id = str(data.get("paciente_id", "")).strip()
    if not es_object_id_valido(paciente_id):
        errores.append("El paciente_id debe ser un ObjectId válido")

    errores.extend(validar_formato_medicamento(data))
    return errores


def verificar_paciente_existe(paciente_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
    return cursor.fetchone() is not None


def verificar_medicamento_duplicado(nombre: str, paciente_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM medicamentos
        WHERE paciente_id = ? AND LOWER(TRIM(nombre)) = LOWER(TRIM(?))
        """,
        (paciente_id, nombre)
    )
    return cursor.fetchone() is not None


def validar_recordatorio(data: dict) -> list:
    errores = []

    campos_obligatorios = {
        "medicamento_id": "La id del medicamento es obligatoria",
        "hora_recordatorio": "Favor ingresar la hora del recordatorio",
        "fecha_inicio": "Se requiere la fecha de inicio"
    }

    for campo, mensaje in campos_obligatorios.items():
        valor = data.get(campo, "")
        if valor is None or str(valor).strip() == "":
            errores.append(mensaje)

    if errores:
        return errores

    medicamento_id = str(data.get("medicamento_id", "")).strip()
    if not es_object_id_valido(medicamento_id):
        errores.append("El medicamento_id debe ser un ObjectId válido")

    try:
        datetime.strptime(data["hora_recordatorio"], "%H:%M")
    except ValueError:
        errores.append("La hora del recordatorio debe tener formato HH:MM")

    try:
        datetime.strptime(data["fecha_inicio"], "%m/%d/%Y")
    except ValueError:
        errores.append("La fecha de inicio debe tener formato mm/dd/yyyy")

    if "activo" in data and str(data["activo"]).strip() != "":
        try:
            activo = int(data["activo"])
            if activo not in [0, 1]:
                errores.append("El campo activo debe ser 0 o 1")
        except (ValueError, TypeError):
            errores.append("El campo activo debe ser un número entero válido")

    return errores


def verificar_medicamento_existe(medicamento_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM medicamentos WHERE id = ?", (medicamento_id,))
    resultado = cursor.fetchone()
    return resultado is not None
