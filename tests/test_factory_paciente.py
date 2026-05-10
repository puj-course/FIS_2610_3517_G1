import os
import sys

# Clave fija para tests.
# El middleware usa os.getenv("SECRET_KEY") para validar el token.
# generate_jwt usa backend.auth.SECRET_KEY.
# Ambas deben coincidir para que TestClient pase por autenticación.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-medtrack"

# Agregamos la raíz del proyecto al path para que pytest pueda importar backend
# correctamente cuando se ejecuta desde Git Bash.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.factories.paciente_factory import PacienteGeneralFactory, PacienteGeneral
from backend.main import app
from backend.auth import generate_jwt
import backend.auth as auth_module

auth_module.SECRET_KEY = os.environ["SECRET_KEY"]
from fastapi.testclient import TestClient


# TestClient = cliente HTTP falso que llama al endpoint sin levantar un servidor real.
# Es parecido a usar Postman, pero desde código.
client = TestClient(app)


def datos_validos():
    """
    Datos válidos base para construir y registrar un paciente.

    Se usan en pruebas de fábrica y en pruebas del endpoint.
    """
    return {
        "nombres": "Laura",
        "apellidos": "Gomez",
        "fecha_nacimiento": "05/10/1990",
        "genero": "Femenino",
        "tipo_documento": "CC",
        "numero_documento": "1020304050",
        "telefono_contacto": "3001234567",
        "eps_aseguradora": "Sura",
        "diagnostico_principal": "Hipertension",
    }


def headers_auth():
    """
    Construye el header Authorization para las pruebas del endpoint.

    La ruta POST /pacientes ahora está protegida. Si no mandamos un
    Bearer token válido, la petición se queda en 403 Forbidden y no llega
    a probar la lógica de pacientes.

    Por eso usamos generate_jwt(), que es la función real del proyecto.
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
    Resultado falso de MongoDB.

    insert_one() normalmente devuelve un objeto con inserted_id.
    Solo necesitamos ese atributo para que la ruta pueda construir
    la respuesta.
    """
    inserted_id = "paciente-test-id"


class PacientesColFalsa:
    """
    Colección falsa para simular pacientes_col.

    Esta clase evita que los tests dependan de MongoDB Atlas.
    Además permite inspeccionar el documento que la ruta intentó guardar.
    """

    def __init__(self, paciente_existente=None):
        self.paciente_existente = paciente_existente
        self.documento_insertado = None
        self.filtro_busqueda = None

    def find_one(self, filtro):
        """
        Simula la búsqueda de duplicados.

        Si paciente_existente es None, la ruta entiende que no hay duplicado.
        Si paciente_existente contiene un dict, la ruta entiende que el paciente
        ya existe y debe responder 409.
        """
        self.filtro_busqueda = filtro
        return self.paciente_existente

    def insert_one(self, documento):
        """
        Simula la inserción de un paciente.

        Guardamos el documento para verificar que la fábrica y la ruta
        construyen correctamente los datos.
        """
        self.documento_insertado = documento
        return ResultadoInsertOneFalso()


# BLOQUE A — PRUEBAS DE LA FÁBRICA SOLA
# Sin HTTP. Sin base de datos. Solo probamos que la fábrica
# construye objetos bien.


def test_fabrica_devuelve_paciente_general():
    """
    PRUEBA BÁSICA: la fábrica debe devolver un objeto PacienteGeneral.

    Paso a paso:
    1. Creamos la fábrica.
    2. Le pedimos que construya un paciente con datos válidos.
    3. Verificamos que el resultado sea una instancia de PacienteGeneral.
    """
    fabrica = PacienteGeneralFactory()

    paciente = fabrica.crear(datos_validos())

    assert isinstance(paciente, PacienteGeneral)


def test_fabrica_limpia_espacios_en_blanco():
    """
    La fábrica debe quitar espacios al inicio y al final de los campos.

    Esto es normalización:
    "  Laura  " debe quedar "Laura".

    Importancia:
    El criterio de aceptación indica que la normalización debe ocurrir en la
    fábrica, no en la ruta ni en la base de datos.
    """
    fabrica = PacienteGeneralFactory()

    data = datos_validos()
    data["nombres"] = "  Laura  "
    data["apellidos"] = "  Gomez  "

    paciente = fabrica.crear(data)

    assert paciente.nombres == "Laura"
    assert paciente.apellidos == "Gomez"


def test_fabrica_maneja_campos_opcionales_ausentes():
    """
    alergias_conocidas y observaciones_adicionales son opcionales.

    Si no vienen en el diccionario, la fábrica debe poner una cadena vacía
    en vez de lanzar un KeyError.
    """
    fabrica = PacienteGeneralFactory()

    paciente = fabrica.crear(datos_validos())

    assert paciente.alergias_conocidas == ""
    assert paciente.observaciones_adicionales == ""


def test_to_tuple_tiene_11_elementos_en_orden_correcto():
    """
    El método como_tupla() debe devolver exactamente 11 valores.

    Aunque la ruta actual de pacientes usa MongoDB, este método sigue siendo
    parte de la fábrica y puede ser usado por compatibilidad o por pruebas
    antiguas. Por eso se conserva esta verificación.

    El orden importa porque originalmente se usaba para INSERT en SQLite.
    """
    fabrica = PacienteGeneralFactory()
    paciente = fabrica.crear(datos_validos())

    tupla = paciente.como_tupla()

    assert len(tupla) == 11
    assert tupla[0] == "Laura"
    assert tupla[1] == "Gomez"
    assert tupla[4] == "CC"
    assert tupla[5] == "1020304050"


# BLOQUE B — PRUEBAS DEL ENDPOINT CON HTTP
# Aquí simulamos peticiones reales al endpoint POST /pacientes.
# No usamos MongoDB real: reemplazamos pacientes_col por una colección falsa.


def test_caso_valido_endpoint_responde_201(monkeypatch):
    """
    CASO VÁLIDO: enviar todos los campos correctos.

    El endpoint debe:
    1. Recibir un token válido.
    2. Pasar la validación del body.
    3. Obtener el cuidador_id desde el JWT.
    4. Verificar que no hay duplicado en pacientes_col.
    5. Construir el paciente con la fábrica.
    6. Guardar el documento en pacientes_col.
    7. Responder 201 con mensaje de éxito y paciente_id.

    201 = Created. Significa que se creó el recurso.
    """
    pacientes_col_falsa = PacientesColFalsa(paciente_existente=None)

    monkeypatch.setattr(
        "backend.routes.patient_route.pacientes_col",
        pacientes_col_falsa
    )

    response = client.post(
        "/pacientes",
        json=datos_validos(),
        headers=headers_auth()
    )

    assert response.status_code == 201

    body = response.json()
    assert body["message"] == "Paciente registrado exitosamente"
    assert body["paciente_id"] == "paciente-test-id"

    documento = pacientes_col_falsa.documento_insertado

    assert documento is not None
    assert documento["nombres"] == "Laura"
    assert documento["apellidos"] == "Gomez"
    assert documento["numero_documento"] == "1020304050"
    assert documento["cuidador_id"] == "cuidador-test-id"


def test_campo_nombres_vacio_responde_400():
    """
    CASO INVÁLIDO: nombres vacío.

    Como la ruta está protegida, enviamos un token válido.
    Así la petición no se bloquea por autenticación y alcanza la validación
    del body.

    Debe responder 400 Bad Request.
    """
    data = datos_validos()
    data["nombres"] = ""

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "El nombre es obligatorio" in response.json()["detail"]


def test_falta_campo_obligatorio_responde_400():
    """
    CASO INVÁLIDO: falta un campo obligatorio.

    Si el body llega sin eps_aseguradora, la validación debe fallar
    con 400.
    """
    data = datos_validos()
    del data["eps_aseguradora"]

    response = client.post(
        "/pacientes",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "La EPS/aseguradora es obligatoria" in response.json()["detail"]


def test_body_casi_vacio_responde_400_con_multiples_errores():
    """
    CASO INVÁLIDO EXTREMO: body con un solo campo.

    Si alguien manda solo {"nombres": "Laura"} sin el resto de campos,
    deben aparecer múltiples errores de validación.
    """
    response = client.post(
        "/pacientes",
        json={"nombres": "Laura"},
        headers=headers_auth()
    )

    assert response.status_code == 400

    errores = response.json()["detail"]
    assert len(errores) > 1


def test_caso_duplicado_responde_409(monkeypatch):
    """
    CASO DUPLICADO: el paciente ya existe.

    Simulamos que pacientes_col.find_one() encuentra un paciente con el mismo:
    - tipo_documento
    - numero_documento
    - cuidador_id

    En ese caso, el endpoint debe responder 409 Conflict.
    """
    data = datos_validos()

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
    assert "Ya existe un paciente con ese documento" in response.json()["detail"]
