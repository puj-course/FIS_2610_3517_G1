# test_recordatorio.py
import os
import sys
import sqlite3
import pytest

# Clave fija para tests.
# El middleware de autenticación valida los JWT usando os.getenv("SECRET_KEY").
# generate_jwt usa backend.auth.SECRET_KEY.
# Por eso ambas claves deben coincidir durante las pruebas.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-medtrack"

from bson import ObjectId
from fastapi.testclient import TestClient

# Agregamos la raíz del proyecto al path para que pytest pueda importar backend
# correctamente cuando se ejecuta desde Git Bash.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import validar_recordatorio, verificar_medicamento_existe
from backend.main import app
from backend.auth import generate_jwt
import backend.auth as auth_module


# Aseguramos que los tokens se firmen con la misma clave que usa el middleware.
auth_module.SECRET_KEY = os.environ["SECRET_KEY"]

# TestClient = cliente HTTP falso que permite probar endpoints de FastAPI
# sin levantar el servidor con uvicorn.
client = TestClient(app)


PACIENTE_ID_VALIDO = "507f1f77bcf86cd799439011"
MEDICAMENTO_ID_VALIDO = "507f1f77bcf86cd799439012"
RECORDATORIO_ID_VALIDO = "507f1f77bcf86cd799439013"


def headers_auth():
    """
    Construye el header Authorization para las pruebas HTTP.

    reminder_route.py no tiene Depends(security), pero main.py sí tiene
    AuthenticationMiddleware global. Por eso, si no enviamos un token válido,
    el request puede ser rechazado antes de llegar a la ruta.
    """
    token = generate_jwt(
        "cuidador-test-id",
        "admin@medtrack.com",
        "administrador"
    )

    return {
        "Authorization": f"Bearer {token}"
    }


def recordatorio_valido():
    """
    Datos base válidos para crear un recordatorio.

    Importante:
    medicamento_id ahora debe ser un ObjectId válido, porque la ruta busca
    el medicamento en MongoDB usando ObjectId(medicamento_id).
    """
    return {
        "medicamento_id": MEDICAMENTO_ID_VALIDO,
        "hora_recordatorio": "08:30",
        "fecha_inicio": "03/25/2026",
        "activo": 1,
        "observaciones": "Prueba",
    }


# =========================
# FUNCIONES AUXILIARES LEGADAS PARA SQLITE
# =========================

def crear_tabla_medicamentos(conn):
    """
    Crea una tabla medicamentos en SQLite en memoria.

    Esta función se conserva porque verificar_medicamento_existe sigue siendo
    una función legada de validaciones.py que recibe una conexión SQLite.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT NOT NULL,
            frecuencia TEXT NOT NULL,
            horario TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            observaciones TEXT,
            paciente_id INTEGER NOT NULL
        )
    """)

    conn.commit()


# =========================
# COLECCIONES FALSAS PARA MONGODB
# =========================

class ResultadoInsertOneFalso:
    """
    Resultado falso de MongoDB.

    insert_one() normalmente devuelve un objeto con inserted_id.
    Solo necesitamos ese atributo para verificar la respuesta del endpoint.
    """
    inserted_id = RECORDATORIO_ID_VALIDO


class ColeccionFalsa:
    """
    Colección falsa para simular una colección de MongoDB.

    Permite probar las rutas sin conectarse a MongoDB Atlas.
    Implementa los métodos que usa reminder_route.py:
    - find_one()
    - find()
    - insert_one()
    - update_one()
    """

    def __init__(self, documentos=None):
        self.documentos = documentos or []
        self.documento_insertado = None
        self.filtro_find_one = None
        self.filtro_find = None
        self.filtro_update = None
        self.update_aplicado = None

    def _coincide(self, documento, filtro):
        """
        Verifica si un documento cumple un filtro simple de igualdad.

        Se permite comparar valores equivalentes aunque uno sea ObjectId y otro str,
        porque las rutas convierten algunos IDs con str(ObjectId(...)).
        """
        filtro = filtro or {}

        for clave, valor in filtro.items():
            valor_documento = documento.get(clave)

            if valor_documento != valor and str(valor_documento) != str(valor):
                return False
        return True

    def find_one(self, filtro):
        """
        Simula find_one() de MongoDB.

        Retorna el primer documento que cumpla el filtro.
        Si no encuentra ninguno, retorna None.
        """
        self.filtro_find_one = filtro

        for documento in self.documentos:
            if self._coincide(documento, filtro):
                return documento

        return None

    def find(self, filtro=None):
        """
        Simula find() de MongoDB.

        Retorna una lista de documentos que cumplen el filtro.
        """
        self.filtro_find = filtro or {}

        return [
            documento
            for documento in self.documentos
            if self._coincide(documento, self.filtro_find)
        ]

    def insert_one(self, documento):
        """
        Simula insert_one() de MongoDB.

        Guarda el documento en memoria para poder verificar qué intentó insertar
        la ruta.
        """
        self.documento_insertado = documento
        self.documentos.append(documento)

        return ResultadoInsertOneFalso()

    def update_one(self, filtro, update):
        """
        Simula update_one() de MongoDB.

        Se usa para probar el PATCH que marca un recordatorio como tomado.
        Si encuentra un documento que coincide con el filtro, aplica el "$set".
        """
        self.filtro_update = filtro
        self.update_aplicado = update

        for documento in self.documentos:
            if self._coincide(documento, filtro):
                if "$set" in update:
                    documento.update(update["$set"])

                class Resultado:
                    matched_count = 1
                    modified_count = 1

                return Resultado()

        class Resultado:
            matched_count = 0
            modified_count = 0

        return Resultado()


def medicamento_mongo():
    """
    Documento de medicamento simulado en MongoDB.

    La ruta crear_recordatorio necesita que el medicamento exista y tenga
    paciente_id asociado.
    """
    return {
        "_id": ObjectId(MEDICAMENTO_ID_VALIDO),
        "nombre": "Aspirina",
        "dosis": "1 tableta",
        "paciente_id": PACIENTE_ID_VALIDO
    }


def paciente_mongo():
    """
    Documento de paciente simulado en MongoDB.
    """
    return {
        "_id": ObjectId(PACIENTE_ID_VALIDO),
        "nombres": "Ana",
        "apellidos": "Lopez"
    }


def recordatorio_mongo():
    """
    Documento de recordatorio simulado en MongoDB.
    """
    return {
        "_id": ObjectId(RECORDATORIO_ID_VALIDO),
        "medicamento_id": MEDICAMENTO_ID_VALIDO,
        "paciente_id": PACIENTE_ID_VALIDO,
        "hora_recordatorio": "08:30",
        "fecha_inicio": "03/25/2026",
        "activo": 1,
        "observaciones": "Prueba",
        "tomado": False
    }


# =========================
# VALIDACIONES
# =========================

def test_validar_recordatorio_exitoso():
    """
    CASO VÁLIDO: todos los campos cumplen las reglas.

    medicamento_id debe ser un ObjectId válido porque la migración a MongoDB
    reemplazó los IDs enteros antiguos.
    """
    data = recordatorio_valido()

    errores = validar_recordatorio(data)

    assert errores == []


def test_medicamento_id_faltante():
    """
    CASO INVÁLIDO: falta medicamento_id.
    """
    data = recordatorio_valido()
    del data["medicamento_id"]

    errores = validar_recordatorio(data)

    assert "La id del medicamento es obligatoria" in errores


def test_hora_recordatorio_vacia():
    """
    CASO INVÁLIDO: hora_recordatorio vacía.
    """
    data = recordatorio_valido()
    data["hora_recordatorio"] = ""

    errores = validar_recordatorio(data)

    assert "Favor ingresar la hora del recordatorio" in errores


def test_fecha_inicio_vacia():
    """
    CASO INVÁLIDO: fecha_inicio vacía.
    """
    data = recordatorio_valido()
    data["fecha_inicio"] = ""

    errores = validar_recordatorio(data)

    assert "Se requiere la fecha de inicio" in errores


def test_medicamento_id_invalido_texto():
    """
    CASO INVÁLIDO: medicamento_id no es ObjectId.

    Antes se esperaba un entero. Después de la migración a MongoDB,
    se espera un ObjectId válido.
    """
    data = recordatorio_valido()
    data["medicamento_id"] = "abc"

    errores = validar_recordatorio(data)

    assert "El medicamento_id debe ser un ObjectId válido" in errores


def test_medicamento_id_invalido_menor_o_igual_a_cero():
    """
    CASO INVÁLIDO: medicamento_id numérico viejo.

    Los IDs enteros ya no son válidos para esta ruta.
    """
    data = recordatorio_valido()
    data["medicamento_id"] = 0

    errores = validar_recordatorio(data)

    assert "El medicamento_id debe ser un ObjectId válido" in errores


def test_hora_formato_invalido():
    """
    CASO INVÁLIDO: hora_recordatorio con formato incorrecto.
    """
    data = recordatorio_valido()
    data["hora_recordatorio"] = "8pm"

    errores = validar_recordatorio(data)

    assert "La hora del recordatorio debe tener formato HH:MM" in errores


def test_fecha_inicio_formato_invalido():
    """
    CASO INVÁLIDO: fecha_inicio con formato incorrecto.

    El proyecto espera fechas en formato mm/dd/yyyy.
    """
    data = recordatorio_valido()
    data["fecha_inicio"] = "2026-03-25"

    errores = validar_recordatorio(data)

    assert "La fecha de inicio debe tener formato mm/dd/yyyy" in errores


def test_activo_invalido():
    """
    CASO INVÁLIDO: activo fuera de los valores permitidos.

    activo solo puede ser 0 o 1.
    """
    data = recordatorio_valido()
    data["activo"] = 5

    errores = validar_recordatorio(data)

    assert "El campo activo debe ser 0 o 1" in errores


def test_hora_limite_inferior():
    """
    CASO VÁLIDO: hora mínima permitida.
    """
    data = recordatorio_valido()
    data["hora_recordatorio"] = "00:00"

    errores = validar_recordatorio(data)

    assert errores == []


def test_hora_limite_superior():
    """
    CASO VÁLIDO: hora máxima permitida.
    """
    data = recordatorio_valido()
    data["hora_recordatorio"] = "23:59"

    errores = validar_recordatorio(data)

    assert errores == []


def test_recordatorio_inactivo():
    """
    CASO VÁLIDO: recordatorio con activo = 0.

    Esto representa un recordatorio inactivo.
    """
    data = recordatorio_valido()
    data["activo"] = 0

    errores = validar_recordatorio(data)

    assert errores == []


# =========================
# BASE DE DATOS LEGADA
# =========================

def test_verificar_medicamento_existe_devuelve_true():
    """
    Prueba unitaria de verificar_medicamento_existe con SQLite en memoria.

    Aunque reminder_route.py ya fue migrado a MongoDB, esta función sigue
    existiendo en validaciones.py. Se conserva esta prueba porque valida
    su comportamiento aislado.
    """
    conn = sqlite3.connect(":memory:")
    crear_tabla_medicamentos(conn)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario,
            fecha_inicio, observaciones, paciente_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Acetaminofen",
        "500 mg",
        "Cada 8 horas",
        "08:00 AM",
        "03/16/2026",
        "Ninguna",
        1,
    ))

    conn.commit()

    resultado = verificar_medicamento_existe(1, conn)

    assert resultado is True

    conn.close()


def test_verificar_medicamento_existe_devuelve_false():
    """
    Prueba unitaria de verificar_medicamento_existe cuando no existe
    el medicamento.
    """
    conn = sqlite3.connect(":memory:")
    crear_tabla_medicamentos(conn)

    resultado = verificar_medicamento_existe(99, conn)

    assert resultado is False

    conn.close()


# =========================
# ENDPOINT POST /recordatorios/
# =========================

def test_post_recordatorio_exitoso(monkeypatch):
    """
    CASO VÁLIDO DEL ENDPOINT POST /recordatorios/.

    La ruta actual ya no usa SQLite. Ahora:
    1. Valida que medicamento_id sea ObjectId.
    2. Busca el medicamento en medicamentos_col.
    3. Obtiene el paciente_id desde el medicamento.
    4. Inserta el recordatorio en recordatorios_col.
    5. Retorna el id creado.

    Por eso se mockean medicamentos_col y recordatorios_col.
    """
    data = recordatorio_valido()

    medicamentos_col_falsa = ColeccionFalsa([
        medicamento_mongo()
    ])

    recordatorios_col_falsa = ColeccionFalsa()

    monkeypatch.setattr(
        "backend.routes.reminder_route.medicamentos_col",
        medicamentos_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.reminder_route.publisher",
        None
    )

    response = client.post(
        "/recordatorios/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Recordatorio creado correctamente"
    assert response.json()["recordatorio_id"] == RECORDATORIO_ID_VALIDO

    documento = recordatorios_col_falsa.documento_insertado

    assert documento is not None
    assert documento["medicamento_id"] == MEDICAMENTO_ID_VALIDO
    assert documento["paciente_id"] == PACIENTE_ID_VALIDO
    assert documento["hora_recordatorio"] == data["hora_recordatorio"].strip()
    assert documento["fecha_inicio"] == data["fecha_inicio"].strip()
    assert documento["activo"] == int(data.get("activo", 1))
    assert documento["observaciones"] == data.get("observaciones", "").strip()
    assert documento["tomado"] is False


def test_post_recordatorio_datos_invalidos():
    """
    CASO INVÁLIDO DEL ENDPOINT POST /recordatorios/.

    Se envía token válido para que el request no se bloquee en el middleware.
    La validación debe fallar porque hora_recordatorio está vacía.
    """
    data = recordatorio_valido()
    data["hora_recordatorio"] = ""

    response = client.post(
        "/recordatorios/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "Favor ingresar la hora del recordatorio" in response.json()["detail"]


def test_post_recordatorio_medicamento_no_existe(monkeypatch):
    """
    CASO INVÁLIDO: el medicamento asociado no existe.

    Simulamos que medicamentos_col.find_one() no encuentra el medicamento.
    La ruta debe responder 404.
    """
    data = recordatorio_valido()

    medicamentos_col_falsa = ColeccionFalsa([])

    monkeypatch.setattr(
        "backend.routes.reminder_route.medicamentos_col",
        medicamentos_col_falsa
    )

    response = client.post(
        "/recordatorios/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El medicamento no existe"


# =========================
# ENDPOINT GET /recordatorios/{paciente_id}
# =========================

def test_get_recordatorios_lista_vacia(monkeypatch):
    """
    CASO SIN REGISTROS: el paciente no tiene recordatorios.

    La ruta actual no consulta SQLite ni valida si el paciente existe.
    Solo busca recordatorios_col.find({"paciente_id": paciente_id}).
    Si no hay resultados, retorna una lista vacía.
    """
    recordatorios_col_falsa = ColeccionFalsa([])

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    response = client.get(
        f"/recordatorios/{PACIENTE_ID_VALIDO}",
        headers=headers_auth()
    )

    assert response.status_code == 200
    assert response.json() == {"recordatorios": []}


def test_get_recordatorios_exitoso(monkeypatch):
    """
    CASO VÁLIDO: el paciente tiene un recordatorio.

    Se simulan:
    - recordatorios_col con un recordatorio activo.
    - medicamentos_col con el medicamento asociado.

    La ruta debe serializar el recordatorio incluyendo datos del medicamento.
    """
    recordatorios_col_falsa = ColeccionFalsa([
        recordatorio_mongo()
    ])

    medicamentos_col_falsa = ColeccionFalsa([
        medicamento_mongo()
    ])

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.reminder_route.medicamentos_col",
        medicamentos_col_falsa
    )

    response = client.get(
        f"/recordatorios/{PACIENTE_ID_VALIDO}",
        headers=headers_auth()
    )

    assert response.status_code == 200

    cuerpo = response.json()

    assert "recordatorios" in cuerpo
    assert len(cuerpo["recordatorios"]) == 1
    assert cuerpo["recordatorios"][0]["medicamento_nombre"] == "Aspirina"
    assert cuerpo["recordatorios"][0]["dosis"] == "1 tableta"
    assert cuerpo["recordatorios"][0]["hora_recordatorio"] == "08:30"
    assert cuerpo["recordatorios"][0]["paciente_id"] == PACIENTE_ID_VALIDO


# =========================
# ENDPOINT GET /recordatorios/panel-dia
# =========================

def test_get_panel_dia_exitoso(monkeypatch):
    """
    CASO VÁLIDO: panel diario con un paciente y un recordatorio activo.

    Esta prueba cubre la ruta GET /recordatorios/panel-dia.

    Para evitar diferencias entre entornos Linux/Windows al comparar ObjectId
    contra string, el recordatorio se construye usando explícitamente el mismo
    paciente_id que genera paciente_mongo().
    """
    paciente = paciente_mongo()
    medicamento = medicamento_mongo()
    recordatorio = recordatorio_mongo()

    paciente_id = str(paciente["_id"])
    medicamento_id = str(medicamento["_id"])

    # Forzamos relación consistente entre paciente, medicamento y recordatorio.
    recordatorio["paciente_id"] = paciente_id
    recordatorio["medicamento_id"] = medicamento_id
    recordatorio["activo"] = 1
    recordatorio["tomado"] = False

    pacientes_col_falsa = ColeccionFalsa([
        paciente
    ])

    recordatorios_col_falsa = ColeccionFalsa([
        recordatorio
    ])

    medicamentos_col_falsa = ColeccionFalsa([
        medicamento
    ])

    monkeypatch.setattr(
        "backend.routes.reminder_route.pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.reminder_route.medicamentos_col",
        medicamentos_col_falsa
    )

    # Verificación previa del fake: antes de llamar la ruta, debe existir
    # un recordatorio activo asociado al paciente.
    assert len(recordatorios_col_falsa.find({
        "paciente_id": paciente_id,
        "activo": 1
    })) == 1

    response = client.get(
        "/recordatorios/panel-dia",
        headers=headers_auth()
    )

    assert response.status_code == 200

    cuerpo = response.json()

    assert "panel" in cuerpo
    assert len(cuerpo["panel"]) == 1
    assert cuerpo["panel"][0]["paciente_id"] == paciente_id
    assert cuerpo["panel"][0]["nombres"] == "Ana"
    assert cuerpo["panel"][0]["apellidos"] == "Lopez"
    assert len(cuerpo["panel"][0]["medicamentos"]) == 1
    assert cuerpo["panel"][0]["medicamentos"][0]["medicamento"] == "Aspirina"
    assert cuerpo["panel"][0]["medicamentos"][0]["dosis"] == "1 tableta"
    assert cuerpo["panel"][0]["medicamentos"][0]["hora"] == "08:30"
    assert cuerpo["panel"][0]["medicamentos"][0]["tomado"] is False

def test_get_recordatorios_retrasados_exitoso(monkeypatch):
    """
    CASO VÁLIDO: consulta de recordatorios retrasados.

    En esta versión se consideran retrasados los recordatorios activos
    que todavía no han sido marcados como tomados.
    """
    recordatorios_col_falsa = ColeccionFalsa([
        recordatorio_mongo()
    ])

    medicamentos_col_falsa = ColeccionFalsa([
        medicamento_mongo()
    ])

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.reminder_route.medicamentos_col",
        medicamentos_col_falsa
    )

    response = client.get(
        f"/recordatorios/retrasados/{PACIENTE_ID_VALIDO}",
        headers=headers_auth()
    )

    assert response.status_code == 200

    cuerpo = response.json()

    assert "recordatorios_retrasados" in cuerpo
    assert len(cuerpo["recordatorios_retrasados"]) == 1
    assert cuerpo["recordatorios_retrasados"][0]["medicamento_nombre"] == "Aspirina"
    assert cuerpo["recordatorios_retrasados"][0]["tomado"] is False


def test_patch_recordatorio_tomado_exitoso(monkeypatch):
    """
    CASO VÁLIDO: marcar un recordatorio como tomado.

    La ruta debe actualizar el campo tomado a True usando update_one().
    """
    recordatorios_col_falsa = ColeccionFalsa([
        recordatorio_mongo()
    ])

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    response = client.patch(
        f"/recordatorios/{RECORDATORIO_ID_VALIDO}/tomado",
        headers=headers_auth()
    )

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Recordatorio marcado como tomado correctamente"
    assert response.json()["recordatorio_id"] == RECORDATORIO_ID_VALIDO

    assert recordatorios_col_falsa.documentos[0]["tomado"] is True


def test_patch_recordatorio_tomado_id_invalido():
    """
    CASO INVÁLIDO: el id del recordatorio no es un ObjectId válido.
    """
    response = client.patch(
        "/recordatorios/id-invalido/tomado",
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "ID de recordatorio inválido"


def test_patch_recordatorio_tomado_no_encontrado(monkeypatch):
    """
    CASO INVÁLIDO: el id tiene formato válido, pero no existe en la colección.
    """
    recordatorios_col_falsa = ColeccionFalsa([])

    monkeypatch.setattr(
        "backend.routes.reminder_route.recordatorios_col",
        recordatorios_col_falsa
    )

    response = client.patch(
        f"/recordatorios/{RECORDATORIO_ID_VALIDO}/tomado",
        headers=headers_auth()
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Recordatorio no encontrado"