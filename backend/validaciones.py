# validaciones.py

from datetime import datetime

def validar_paciente(data: dict):
    errores = []

    campos_obligatorios = [
        "nombres",
        "apellidos",
        "fecha_nacimiento",
        "genero",
        "tipo_documento",
        "numero_documento",
        "telefono_contacto",
        "eps_aseguradora",
        "diagnostico_principal"
    ]

    for campo in campos_obligatorios:
        if campo not in data or str(data[campo]).strip() == "":
            errores.append(f"El campo '{campo}' es obligatorio.")

    fecha = data.get("fecha_nacimiento", "").strip()
    if fecha:
        try:
            datetime.strptime(fecha, "%m/%d/%Y")
        except ValueError:
            errores.append("La fecha_nacimiento debe tener formato mm/dd/yyyy.")

    telefono = str(data.get("telefono_contacto", "")).strip()
    if telefono and not telefono.replace("+", "").replace(" ", "").isdigit():
        errores.append("El telefono_contacto debe contener solo números.")

    return errores


def verificar_duplicado(numero_documento, tipo_documento, conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id
        FROM pacientes
        WHERE numero_documento = ? AND tipo_documento = ?
    """, (numero_documento, tipo_documento))

    paciente = cursor.fetchone()
    return paciente is not None
