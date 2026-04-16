# validaciones.py
# Este archivo se encarga de revisar que los datos del paciente esten bien antes de guardarlos en la base de datos
from datetime import datetime


# Opciones validas para tipo de documento y género
TIPOS_DOCUMENTO = ["CC", "TI", "CE", "PA", "RC"]
GENEROS = ["Masculino", "Femenino", "Otro"]

#la función recibe un diccionario y devuelve una lista de errores, si la lista está vacía todo está bien
def validar_paciente(data: dict) -> list:
    # data es el diccionario con los datos que llegaron del formulario
    # la función devuelve una lista de errores, si está vacía todo está bien
    errores = []
    # Estos son los campos que no pueden estar vacíos
    campos_obligatorios = {
    "nombres": "El nombre es obligatorio",
    "apellidos": "Los apellidos son obligatorios",
    "fecha_nacimiento": "La fecha de nacimiento es obligatoria",
    "genero": "El género es obligatorio",
    "tipo_documento": "El tipo de documento es obligatorio",
    "numero_documento": "El número de documento es obligatorio",
    "telefono_contacto": "El teléfono de contacto es obligatorio",  # cambiado
    "eps_aseguradora": "La EPS/aseguradora es obligatoria",          # cambiado
    "diagnostico_principal": "El diagnóstico principal es obligatorio",
    }

    # Revisa uno por uno si el campo llegó vacío o no llegó
    #items se encarga de retornar el par clave-valor del diccionario, entonces campo es la clave y mensaje es el valor

    for campo, mensaje in campos_obligatorios.items():
        #de lo que tengo en mi UI reviso campo a campo y obtengo el valor, si no hay devuelve string vacío
        valor = data.get(campo, "")
        #me permite decirle a la funcion que faltó un campo. .strip elimina los espacios en blanco al inicio y al final, entonces si el usuario solo puso espacios, también lo consideramos vacío
        if not valor or str(valor).strip() == "":
            errores.append(mensaje)

    # Si ya hay campos vacíos no seguimos, pues ya sabemos que no tenemos datos completos para validar lo demás
    if errores:
        return errores

    # Revisa que la fecha tenga el formato mm/dd/yyyy y que coherente 
    try:
        fecha = datetime.strptime(data["fecha_nacimiento"], "%m/%d/%Y")
        if fecha > datetime.now():
            errores.append("La fecha de nacimiento no puede ser futura")
    except ValueError:
        errores.append("La fecha de nacimiento debe tener formato mm/dd/yyyy")

    # Revisa que el genero sea una opción válida
    if data["genero"] not in GENEROS:
        errores.append(f"El género debe ser uno de: {', '.join(GENEROS)}")

    # Revisa que el tipo de documento sea una opción válida
    if data["tipo_documento"] not in TIPOS_DOCUMENTO:
        errores.append(f"El tipo de documento debe ser uno de: {', '.join(TIPOS_DOCUMENTO)}")

    # El número de documento solo puede tener números
    if not data["numero_documento"].isdigit():
        errores.append("El número de documento debe contener solo números")

    # El teléfono solo puede tener números y debe tener entre 7 y 10 dígitos
    telefono = data["telefono_contacto"].strip()  
    #si no es numero o si no tiene entre 7 y 10 dígitos, entonces es un error
    if not telefono.isdigit() or not (7 <= len(telefono) <= 10):
        errores.append("El teléfono debe contener solo números y tener entre 7 y 10 dígitos")

    return errores

def verificar_duplicado(numero_documento: str, tipo_documento: str, conn) -> bool:
    # Busca en la base de datos si ya hay un paciente con ese documento
    # Devuelve True si ya existe, False si no

    cursor = conn.cursor()

    # Arma la consulta con los datos recibidos
    cursor.execute(
        "SELECT id FROM pacientes WHERE numero_documento = ? AND tipo_documento = ?",
        (numero_documento, tipo_documento)
    )

    # Si encontró algo, es duplicado
    resultado = cursor.fetchone()
    return resultado is not None
# Validaciones adicionales de formato para medicamento — issue #195
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

# Lógica de creación de esquema de validación de medicamentos (HU'09)
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

    try:
        paciente_id = int(data["paciente_id"])
        if paciente_id <= 0:
            errores.append("El paciente_id debe ser un número mayor que 0")
    except (ValueError, TypeError):
        errores.append("El paciente_id debe ser un número entero válido")

    errores.extend(validar_formato_medicamento(data))
    return errores
def verificar_paciente_existe(paciente_id: int, conn) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,))
    return cursor.fetchone() is not None # Devuelve true o false dependiendo si el paciente existe en la database
#
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
# Función asociada a los recordatorios (HU'15, SUB #251)

def validar_recordatorio(data: dict) -> list:
	# data es el diccionario con los datos del rcordatorio
	# la función devuelve una lista de errores; si está vacía, todo OK
	errores = []

	# Campos obligatorios del recordatorio
	campos_obligatorios = {
		"medicamento_id": "La id del medicamento es obligatoria",
		"hora_recordatorio": "Favor ingresar la hora del recordatorio",
		"fecha_inicio": "Se requiere la fecha de inicio"
	}

	# Para revisar que los campos obligatorios hayan llegado y no estén vacíos
	for campo, mensaje in campos_obligatorios.items():
		valor = data.get(campo, "")
		if valor is None or str(valor).strip() == "":
			errores.append(mensaje)

	# No se sigue validando lo demás si faltan campos obligatorios
	if errores:
		return errores

	# Validar que la id del medicamento sea un entero válido > 0
	try:
		medicamento_id = int(data["medicamento_id"])
		if medicamento_id <= 0:
			errores.append("La id del medicamento debe ser un número > 0")
	except (ValueError, TypeError):
		errores.append("La id del del medicamento debe ser un entero válido")

	# Validar formato de hora_recordatorio: HH:MM
	try:
		datetime.strptime(data["hora_recordatorio"], "%H:%M")
	except ValueError:
		errores.append("La hora del recordatorio debe tener formato HH:MM")

	# Validar formato de fecha_inicio mm/dd/yyyy
	try:
		datetime.strptime(data["fecha_inicio"], "%m/%d/%Y")
	except ValueError:
		errores.append("La fecha de inicio debe tener formato mm/dd/yyyy")


	# Validar activo solo si llega en el JSON
	if "activo" in data and str(data["activo"]).strip() != "":
		try:
			activo = int(data["activo"])
			if activo not in [0, 1]:
				errores.append("El campo activo debe ser 0 o 1")
		except (ValueError, TypeError):
			errores.append("El campo activo debe ser un número entero válido")
	return errores

	# Verificar la existencia del medicamento en la BD
	# Devuelve True si existe, False si no
def verificar_medicamento_existe(medicamento_id: int, conn) -> bool:
	cursor = conn.cursor() # conn recibe la conexion a SQLite
	cursor.execute("SELECT id FROM medicamentos WHERE id = ?", (medicamento_id,))
	resultado = cursor.fetchone() # fetchone trae una sola fila
	return resultado is not None

def validar_historial_toma(data: dict) -> list:
    """
    Valida los datos de entrada para registrar una toma en el historial.
    """
    errores = []

    # Campos obligatorios
    if not data.get("paciente_id"):
        errores.append("paciente_id es obligatorio")
    if not data.get("medicamento_id"):
        errores.append("medicamento_id es obligatorio")
    if not str(data.get("fecha_programada", "")).strip():
        errores.append("fecha_programada es obligatoria")

    if errores:
        return errores

    # paciente_id debe ser entero > 0
    try:
        if int(data["paciente_id"]) <= 0:
            errores.append("paciente_id debe ser mayor que 0")
    except (ValueError, TypeError):
        errores.append("paciente_id debe ser un entero válido")

    # medicamento_id debe ser entero > 0
    try:
        if int(data["medicamento_id"]) <= 0:
            errores.append("medicamento_id debe ser mayor que 0")
    except (ValueError, TypeError):
        errores.append("medicamento_id debe ser un entero válido")

    # Formato de fecha_programada: YYYY-MM-DD HH:MM:SS
    try:
        datetime.strptime(data["fecha_programada"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        errores.append("fecha_programada debe tener formato YYYY-MM-DD HH:MM:SS")

    # Si viene fecha_hora_toma, también debe tener el formato correcto
    fecha_toma = data.get("fecha_hora_toma")
    if fecha_toma and str(fecha_toma).strip():
        try:
            datetime.strptime(str(fecha_toma), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            errores.append("fecha_hora_toma debe tener formato YYYY-MM-DD HH:MM:SS")

    return errores
