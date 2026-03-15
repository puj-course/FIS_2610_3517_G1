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
    query = f"SELECT id FROM pacientes WHERE numero_documento = '{numero_documento}' AND tipo_documento = '{tipo_documento}'"
    cursor.execute(query)

    # Si encontró algo, es duplicado
    resultado = cursor.fetchone()
    return resultado is not None
# Validaciones adicionales de formato para medicamento — issue #195
def validar_formato_medicamento(data: dict) -> list:
    """
    Complementa validar_medicamento() con reglas de formato:
      - El nombre debe tener al menos 2 caracteres
      - La fecha_inicio debe tener formato mm/dd/yyyy y no ser anterior al 2000
    Devuelve lista de errores; vacía si todo está bien.
    """
    errores = []

    # El nombre no puede ser un solo carácter
    nombre = str(data.get("nombre", "")).strip()
    if nombre and len(nombre) < 2:
        errores.append("El nombre del medicamento debe tener al menos 2 caracteres")

    # La fecha debe tener formato mm/dd/yyyy y no ser anterior al año 2000
    fecha = str(data.get("fecha_inicio", "")).strip()
    if fecha:
        try:
            fecha_parsed = datetime.strptime(fecha, "%m/%d/%Y")
            if fecha_parsed < datetime(2000, 1, 1):
                errores.append("La fecha de inicio no puede ser anterior al año 2000")
        except ValueError:
            errores.append("La fecha de inicio debe tener formato mm/dd/yyyy")

    return errores


# Lógica de creación de esquema de validación de medicamentos (HU'09)
def validar_medicamento(data: dict) -> list:
    errores = []
    campos_obligatorios = {
        "nombre": "El nombre del medicamento es obligatorio",
        "dosis": "La dosis es obligatoria",
        "frecuencia": "La frecuencia es obligatoria",
        "horario": "El horario de toma es obligatorio",
        "fecha_inicio": "La fecha de inicio es obligatoria",
        "paciente_id": "El paciente_id es obligatorio"
    }
    for campo, mensaje in campos_obligatorios.items():
        valor = data.get(campo, "")
        if valor is None or str(valor).strip() == "":
            errores.append(mensaje)
    if errores:
        return errores
    try:
        paciente_id = int(data["paciente_id"])
        if paciente_id <= 0:
            errores.append("El paciente_id debe ser un número mayor que 0")
    except (ValueError, TypeError):
        errores.append("El paciente_id debe ser un número entero válido")
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