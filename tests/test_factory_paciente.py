import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from unittest.mock import patch, MagicMock

# La fabrica que creamos en la HU-27
from backend.factories.paciente_factory import PacienteGeneralFactory, PacienteGeneral

# TestClient = cliente HTTP falso que llama al endpoint sin levantar un servidor real
from fastapi.testclient import TestClient

# app es tu aplicacion FastAPI (en main.py)
from backend.main import app

# Creamos el cliente una sola vez. Es como tener Postman pero en codigo.
client = TestClient(app)


def datos_validos():
    return {
        "nombres":               "Laura",
        "apellidos":             "Gomez",
        "fecha_nacimiento":      "05/10/1990",
        "genero":                "Femenino",
        "tipo_documento":        "CC",
        "numero_documento":      "1020304050",
        "telefono_contacto":     "3001234567",
        "eps_aseguradora":       "Sura",
        "diagnostico_principal": "Hipertension",
    }


# BLOQUE A — PRUEBAS DE LA FABRICA SOLA
# Sin HTTP. Sin base de datos. Solo probamos que la fabrica
# construye objetos bien.


def test_fabrica_devuelve_paciente_general():
    """
    PRUEBA MAS BASICA: la fabrica debe devolver un objeto PacienteGeneral.

    Paso a paso:
    1. Creamos la fabrica
    2. Le pedimos que construya un paciente con datos validos
    3. Verificamos que lo que devolvio es del tipo PacienteGeneral
    """
    # Paso 1: crear la fabrica
    fabrica = PacienteGeneralFactory()

    # Paso 2: construir el paciente
    paciente = fabrica.crear(datos_validos())

    # Paso 3: verificar el tipo
    # isinstance(x, Y) devuelve True si x es del tipo Y
    assert isinstance(paciente, PacienteGeneral)
    # Si esto falla, pytest muestra: AssertionError: assert False


def test_fabrica_limpia_espacios_en_blanco():
    """
    La fabrica debe quitar espacios al inicio y al final de los campos.
    Esto es la normalizacion: "  Laura  " debe quedar "Laura".

    Por que importa: el criterio de aceptacion dice que la normalizacion
    debe ocurrir en la fabrica, no en la ruta.
    """
    fabrica = PacienteGeneralFactory()

    # Modificamos los datos para agregar espacios extra
    data = datos_validos()
    data["nombres"] = "  Laura  "    # espacios al inicio y al final
    data["apellidos"] = "  Gomez  "  # idem

    paciente = fabrica.crear(data)

    # Verificamos que el objeto tenga los valores limpios
    assert paciente.nombres == "Laura"   # sin espacios
    assert paciente.apellidos == "Gomez" # sin espacios


def test_fabrica_maneja_campos_opcionales_ausentes():
    """
    alergias_conocidas y observaciones_adicionales son opcionales.
    Si no vienen en el dict, la fabrica debe poner "" (cadena vacia)
    en vez de lanzar un KeyError.

    KeyError es el error que Python lanza cuando buscas una clave
    en un diccionario y no existe. Ej: data["alergias"] cuando
    "alergias" no esta en data.
    """
    fabrica = PacienteGeneralFactory()

    # datos_validos() NO incluye alergias ni observaciones
    paciente = fabrica.crear(datos_validos())

    # Deben existir pero con valor vacio
    assert paciente.alergias_conocidas == ""
    assert paciente.observaciones_adicionales == ""


def test_to_tuple_tiene_11_elementos_en_orden_correcto():
    """
    El metodo como_tupla() del paciente debe devolver exactamente
    11 valores, en el MISMO ORDEN que los ? del INSERT de la BD.

    Por que el orden importa:
    El INSERT dice:
        INSERT INTO pacientes (nombres, apellidos, fecha_nacimiento, ...)
        VALUES (?, ?, ?, ...)
    SQLite asigna el primer ? al primer valor de la tupla, el segundo
    al segundo, etc. Si el orden esta mal, el apellido queda guardado
    en la columna de genero, por ejemplo.
    """
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    # como_tupla() debe devolver una tupla (no una lista, no un dict)
    tupla = paciente.como_tupla()

    # Verificamos la cantidad
    assert len(tupla) == 11

    # Verificamos el orden de algunas posiciones clave
    assert tupla[0] == "Laura"        # nombres va primero
    assert tupla[1] == "Gomez"        # apellidos va segundo
    assert tupla[4] == "CC"           # tipo_documento en posicion 4
    assert tupla[5] == "1020304050"   # numero_documento en posicion 5


# BLOQUE B — PRUEBAS DEL ENDPOINT CON HTTP
# Aqui simulamos peticiones reales al endpoint POST /pacientes.
# Usamos mocks para no necesitar una BD real.

def test_caso_valido_endpoint_responde_201():
    """
    CASO VALIDO: enviar todos los campos correctos.

    El endpoint debe:
    1. Pasar la validacion sin errores
    2. Verificar que no es duplicado (simulamos que no lo es)
    3. Construir el paciente con la fabrica
    4. "Guardar" en BD (simulada)
    5. Responder 201 con el mensaje de exito y el id

    201 = "Created" en HTTP. Significa que se creo el recurso.
    """

    # Creamos la conexion falsa a la BD
    conexion_falsa = MagicMock()

    # cursor_falso es el objeto que ejecuta el SQL
    cursor_falso = MagicMock()

    # Cuando el endpoint pregunte cursor.lastrowid (el id recien insertado),
    # devolvemos 42 (cualquier numero sirve para la prueba)
    cursor_falso.lastrowid = 42

    # Cuando el endpoint llame conexion.cursor(), devolvemos el cursor falso
    conexion_falsa.cursor.return_value = cursor_falso

    # 'with patch' reemplaza las funciones SOLO durante esta prueba
    with patch("backend.routes.patient_route.get_connection",
               return_value=conexion_falsa), \
         patch("backend.routes.patient_route.verificar_duplicado",
               return_value=False):    # False = no es duplicado

        # client.post hace la peticion HTTP al endpoint
        # json=datos_validos() envia el dict como JSON en el body
        response = client.post("/pacientes", json=datos_validos())

    # Verificamos el codigo de estado HTTP
    assert response.status_code == 201

    # response.json() convierte la respuesta JSON a un dict de Python
    body = response.json()
    assert body["message"] == "Paciente registrado exitosamente"
    assert body["paciente_id"] == 42


def test_campo_nombres_vacio_responde_400():
    """
    CASO INVALIDO: nombres vacio.

    Cuando un campo obligatorio esta vacio, la validacion debe
    rechazar la peticion con 400 Bad Request ANTES de tocar la BD.

    400 = "Bad Request". El cliente mando datos incorrectos.

    Esta prueba NO necesita mock de BD porque la validacion
    ocurre antes de que el endpoint abra la conexion.
    """
    data = datos_validos()
    data["nombres"] = ""   # campo obligatorio pero vacio

    response = client.post("/pacientes", json=data)

    # Debe rechazar con 400
    assert response.status_code == 400

    # El mensaje de error debe mencionar el problema
    # response.json()["detail"] es donde FastAPI pone los errores
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_falta_campo_obligatorio_responde_400():
    """
    CASO INVALIDO: falta un campo obligatorio en el body.

    Si el body llega sin eps_aseguradora, debe fallar con 400.
    """
    data = datos_validos()
    del data["eps_aseguradora"]   # eliminamos el campo del dict

    response = client.post("/pacientes", json=data)

    assert response.status_code == 400
    assert "La EPS/aseguradora es obligatoria" in response.json()["detail"]


def test_body_casi_vacio_responde_400_con_multiples_errores():
    """
    CASO INVALIDO EXTREMO: body con un solo campo.

    Si alguien manda solo {"nombres": "Laura"} sin nada mas,
    deben aparecer multiples mensajes de error (uno por cada
    campo faltante).

    Esto simula el curl de prueba que pide la definicion de terminado:
        curl -X POST .../pacientes -d '{"nombres": "Laura"}'
    """
    response = client.post("/pacientes", json={"nombres": "Laura"})

    assert response.status_code == 400

    errores = response.json()["detail"]

    # Debe haber mas de un error (faltan muchos campos)
    assert len(errores) > 1


def test_caso_duplicado_responde_409():
    """
    CASO DUPLICADO: el paciente ya existe en la BD.

    Cuando verificar_duplicado devuelve True, el endpoint debe
    responder 409 Conflict sin intentar hacer el INSERT.

    409 = "Conflict". Ya existe un recurso con esos datos.
    """
    conexion_falsa = MagicMock()

    with patch("backend.routes.patient_route.get_connection",
               return_value=conexion_falsa), \
         patch("backend.routes.patient_route.verificar_duplicado",
               return_value=True):    # True = SI es duplicado

        response = client.post("/pacientes", json=datos_validos())

    assert response.status_code == 409
    assert "Ya existe un paciente con ese documento" in response.json()["detail"]
