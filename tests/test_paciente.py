import os
import sys
import sqlite3

# Clave fija para tests.
# El middleware de autenticación valida los JWT con os.getenv("SECRET_KEY"),
# mientras que generate_jwt usa backend.auth.SECRET_KEY.
# Por eso en pruebas dejamos ambas apuntando a la misma clave.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-medtrack"

from fastapi.testclient import TestClient

# Agregamos la raíz del proyecto al path para que pytest pueda importar backend
# sin depender de cómo se ejecute el comando desde Git Bash.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_paciente, verificar_duplicado
from backend.main import app
from backend.auth import generate_jwt
import backend.auth as auth_module

auth_module.SECRET_KEY = os.environ["SECRET_KEY"]


# TestClient = cliente HTTP falso que permite probar los endpoints de FastAPI
# sin levantar el servidor con uvicorn.
client = TestClient(app)


def paciente_valido():
    """
    Datos base válidos para las pruebas de pacientes.

    Se usan en varios tests para evitar repetir el mismo diccionario.
    Cuando un test necesita probar un caso inválido, modifica una copia
    de estos datos.
    """
    return {
        "nombres": "Juan",
        "apellidos": "Perez",
        "fecha_nacimiento": "01/15/1990",
        "genero": "Masculino",
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension"
    }


def headers_auth():
    """
    Construye un header Authorization válido para las pruebas HTTP.

    Antes los tests llamaban POST /pacientes sin token, pero ahora la ruta
    está protegida con autenticación. Si no se envía un Bearer token válido,
    FastAPI responde 403 antes de llegar a la validación del paciente.

    Por eso generamos un JWT real con la misma función del proyecto.
    Así se prueba el endpoint de forma más cercana al uso real:
    - pasa por AuthenticationMiddleware
    - pasa por HTTPBearer
    - llega a registrar_paciente()
    """
    token = generate_jwt(
        "cuidador-test-id",
        "admin@medtrack.com",
        "administrador"
    )

    return {
        "Authorization": f"Bearer {token}"
    }


class ResultadoInsertOneFalso:
    """
    Resultado falso de insert_one().

    En MongoDB real, insert_one() devuelve un objeto con inserted_id.
    Para no depender de una base real en los tests, simulamos solo ese
    comportamiento mínimo.
    """
    inserted_id = "paciente-test-id"


class PacientesColFalsa:
    """
    Colección falsa para reemplazar pacientes_col durante las pruebas.

    Esta clase simula los métodos de MongoDB que usa patient_route.py:
    - find_one(): para verificar duplicados
    - insert_one(): para guardar el paciente

    Así probamos la lógica de la ruta sin conectarnos a MongoDB Atlas.
    """

    def __init__(self, paciente_existente=None):
        self.paciente_existente = paciente_existente
        self.documento_insertado = None
        self.filtro_busqueda = None

    def find_one(self, filtro):
        """
        Simula la búsqueda de un paciente existente.

        Si paciente_existente es None, significa que no hay duplicado.
        Si paciente_existente tiene un dict, significa que el paciente ya existe.
        """
        self.filtro_busqueda = filtro
        return self.paciente_existente

    def insert_one(self, documento):
        """
        Simula la inserción de un paciente en MongoDB.

        Guardamos el documento en self.documento_insertado para poder
        verificar después qué datos intentó guardar la ruta.
        """
        self.documento_insertado = documento
        return ResultadoInsertOneFalso()


def test_validar_paciente_exitoso():
    """
    CASO VÁLIDO: todos los campos obligatorios cumplen las reglas.

    La función validar_paciente debe devolver una lista vacía de errores.
    """
    data = paciente_valido()
    errores = validar_paciente(data)

    assert errores == []


def test_nombre_vacio():
    """
    CASO INVÁLIDO: nombres vacío.

    El campo nombres es obligatorio, por eso debe aparecer el mensaje
    correspondiente en la lista de errores.
    """
    data = paciente_valido()
    data["nombres"] = ""

    errores = validar_paciente(data)

    assert "El nombre es obligatorio" in errores


def test_apellidos_vacios():
    """
    CASO INVÁLIDO: apellidos vacío.

    El campo apellidos es obligatorio.
    """
    data = paciente_valido()
    data["apellidos"] = ""

    errores = validar_paciente(data)

    assert "Los apellidos son obligatorios" in errores


def test_fecha_invalida():
    """
    CASO INVÁLIDO: fecha con formato incorrecto.

    El proyecto espera fechas en formato mm/dd/yyyy.
    """
    data = paciente_valido()
    data["fecha_nacimiento"] = "1990-01-15"

    errores = validar_paciente(data)

    assert "La fecha de nacimiento debe tener formato mm/dd/yyyy" in errores


def test_fecha_futura():
    """
    CASO INVÁLIDO: fecha de nacimiento futura.

    No debería permitirse registrar un paciente con fecha de nacimiento
    posterior a la fecha actual.
    """
    data = paciente_valido()
    data["fecha_nacimiento"] = "12/31/2099"

    errores = validar_paciente(data)

    assert "La fecha de nacimiento no puede ser futura" in errores


def test_genero_invalido():
    """
    CASO INVÁLIDO: género fuera de las opciones permitidas.
    """
    data = paciente_valido()
    data["genero"] = "Alien"

    errores = validar_paciente(data)

    assert any("El género debe ser uno de" in e for e in errores)


def test_tipo_documento_invalido():
    """
    CASO INVÁLIDO: tipo de documento fuera de las opciones permitidas.
    """
    data = paciente_valido()
    data["tipo_documento"] = "XYZ"

    errores = validar_paciente(data)

    assert any("El tipo de documento debe ser uno de" in e for e in errores)


def test_documento_invalido():
    """
    CASO INVÁLIDO: número de documento con letras.

    La validación espera que el número de documento contenga solo números.
    """
    data = paciente_valido()
    data["numero_documento"] = "ABC123"

    errores = validar_paciente(data)

    assert "El número de documento debe contener solo números" in errores


def test_telefono_invalido():
    """
    CASO INVÁLIDO: teléfono demasiado corto.

    El teléfono debe contener solo números y tener entre 7 y 10 dígitos.
    """
    data = paciente_valido()
    data["telefono_contacto"] = "123"

    errores = validar_paciente(data)

    assert "El teléfono debe contener solo números y tener entre 7 y 10 dígitos" in errores


def test_faltan_campos_obligatorios():
    """
    CASO INVÁLIDO: falta eps_aseguradora.

    Se elimina un campo obligatorio para comprobar que la validación
    lo detecta correctamente.
    """
    data = paciente_valido()
    del data["eps_aseguradora"]

    errores = validar_paciente(data)

    assert "La EPS/aseguradora es obligatoria" in errores


def test_verificar_duplicado_devuelve_true_si_existe():
    """
    Prueba unitaria de verificar_duplicado con SQLite en memoria.

    Aunque la ruta actual de pacientes ya fue migrada a MongoDB,
    esta función sigue existiendo en validaciones.py y estos tests validan
    su comportamiento aislado.

    SQLite en memoria permite probar sin tocar database.db real.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            genero TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            telefono_contacto TEXT NOT NULL,
            eps_aseguradora TEXT,
            diagnostico_principal TEXT,
            alergias_conocidas TEXT,
            observaciones_adicionales TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO pacientes (
            nombres, apellidos, fecha_nacimiento, genero,
            tipo_documento, numero_documento, telefono_contacto,
            eps_aseguradora, diagnostico_principal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Juan", "Perez", "01/15/1990", "Masculino",
        "CC", "12345678", "3001234567", "Sura", "Hipertension"
    ))

    conn.commit()

    resultado = verificar_duplicado("12345678", "CC", conn)

    assert resultado is True
    conn.close()


def test_verificar_duplicado_devuelve_false_si_no_existe():
    """
    Prueba unitaria de verificar_duplicado cuando no hay coincidencias.

    La tabla existe, pero no insertamos ningún paciente con el documento
    consultado. Por eso debe devolver False.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            genero TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            telefono_contacto TEXT NOT NULL,
            eps_aseguradora TEXT,
            diagnostico_principal TEXT,
            alergias_conocidas TEXT,
            observaciones_adicionales TEXT
        )
    """)

    conn.commit()

    resultado = verificar_duplicado("99999999", "CC", conn)

    assert resultado is False
    conn.close()


def test_post_paciente_exitoso(monkeypatch):
    """
    CASO VÁLIDO DEL ENDPOINT POST /pacientes.

    La ruta actual ya no usa SQLite ni get_connection.
    Ahora:
    1. Valida los datos del paciente.
    2. Obtiene el cuidador_id desde el JWT.
    3. Busca duplicados en pacientes_col.
    4. Inserta el documento en pacientes_col.
    5. Devuelve el id generado por MongoDB.

    Por eso aquí se reemplaza pacientes_col por una colección falsa,
    pero se conserva TestClient para probar la llamada HTTP real.
    """
    data = paciente_valido()
    pacientes_col_falsa = PacientesColFalsa(paciente_existente=None)

    monkeypatch.setattr(
        "backend.routes.patient_route.pacientes_col",
        pacientes_col_falsa
    )

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Paciente registrado exitosamente"
    assert response.json()["paciente_id"] == "paciente-test-id"

    documento = pacientes_col_falsa.documento_insertado

    assert documento is not None
    assert documento["nombres"] == data["nombres"]
    assert documento["apellidos"] == data["apellidos"]
    assert documento["numero_documento"] == data["numero_documento"]
    assert documento["cuidador_id"] == "cuidador-test-id"


def test_post_paciente_datos_invalidos():
    """
    CASO INVÁLIDO DEL ENDPOINT POST /pacientes.

    Se envía un token válido para que la petición no sea rechazada por
    autenticación. Así la prueba alcanza la validación del body y debe
    devolver 400 por nombres vacío.
    """
    data = paciente_valido()
    data["nombres"] = ""

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_post_paciente_duplicado(monkeypatch):
    """
    CASO DUPLICADO DEL ENDPOINT POST /pacientes.

    Simulamos que pacientes_col.find_one() encuentra un paciente con el
    mismo tipo_documento, numero_documento y cuidador_id.

    La ruta debe responder 409 Conflict.
    """
    data = paciente_valido()

    pacientes_col_falsa = PacientesColFalsa(
        paciente_existente={
            "_id": "paciente-existente-id",
            "tipo_documento": data["tipo_documento"],
            "numero_documento": data["numero_documento"],
            "cuidador_id": "cuidador-test-id"
        }
    )

    monkeypatch.setattr(
        "backend.routes.patient_route.pacientes_col",
        pacientes_col_falsa
    )

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un paciente con ese documento"