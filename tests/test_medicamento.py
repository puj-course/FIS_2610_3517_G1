# test_medicamento.py
import os
import sys
import sqlite3

# Clave fija para tests.
# El middleware de autenticación valida los JWT con os.getenv("SECRET_KEY").
# generate_jwt usa backend.auth.SECRET_KEY.
# Por eso dejamos ambas claves iguales en pruebas.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-medtrack"

from fastapi.testclient import TestClient

# Agregamos la raíz del proyecto al path para que pytest pueda importar backend
# correctamente cuando se ejecuta desde Git Bash.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.validaciones import (
    validar_medicamento,
    verificar_paciente_existe,
    verificar_medicamento_duplicado
)
from backend.main import app
from backend.auth import generate_jwt
import backend.auth as auth_module


# Aseguramos que los tokens se firmen con la misma clave que usa el middleware.
auth_module.SECRET_KEY = os.environ["SECRET_KEY"]

# TestClient = cliente HTTP falso que permite probar endpoints de FastAPI
# sin levantar el servidor con uvicorn.
client = TestClient(app)


PACIENTE_ID_VALIDO = "507f1f77bcf86cd799439011"


def medicamento_valido():
    """
    Datos base válidos para registrar un medicamento.

    Importante:
    paciente_id ahora debe ser un ObjectId válido porque medication_route.py
    consulta pacientes_col usando ObjectId(paciente_id).
    """
    return {
        "nombre_medicamento": "Acetaminofen",
        "concentracion": "500 mg",
        "forma_farmaceutica": "Tableta",
        "dosis_cantidad": 1,
        "dosis_unidad": "tableta",
        "frecuencia": "Cada 8 horas",
        "fecha_inicio": "03/16/2026",
        "paciente_id": PACIENTE_ID_VALIDO,
        "horarios": ["08:00", "16:00", "00:00"],
        "observaciones": "Tomar después de comer"
    }


def headers_auth():
    """
    Construye el header Authorization para las pruebas del endpoint.

    Aunque medication_route.py no tiene Depends(security), main.py tiene un
    AuthenticationMiddleware global. Si no mandamos un token válido, la petición
    se bloquea antes de llegar al endpoint.
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
    Solo necesitamos ese atributo para verificar la respuesta del endpoint.
    """
    inserted_id = "medicamento-test-id"


class PacientesColFalsa:
    """
    Colección falsa para simular pacientes_col.

    Esta clase reemplaza la colección real de MongoDB durante los tests.
    """

    def __init__(self, paciente_existente=None):
        self.paciente_existente = paciente_existente
        self.filtro_busqueda = None

    def find_one(self, filtro):
        """
        Simula la búsqueda del paciente asociado al medicamento.

        Si paciente_existente es None, la ruta entiende que el paciente no existe.
        Si paciente_existente tiene un dict, la ruta entiende que el paciente existe.
        """
        self.filtro_busqueda = filtro
        return self.paciente_existente


class MedicamentosColFalsa:
    """
    Colección falsa para simular medicamentos_col.

    Esta clase simula:
    - find_one(): búsqueda de medicamento duplicado
    - insert_one(): creación del medicamento
    """

    def __init__(self, medicamento_existente=None):
        self.medicamento_existente = medicamento_existente
        self.documento_insertado = None
        self.filtro_busqueda = None

    def find_one(self, filtro):
        """
        Simula la búsqueda de un medicamento duplicado.
        """
        self.filtro_busqueda = filtro
        return self.medicamento_existente

    def insert_one(self, documento):
        """
        Simula la inserción de un medicamento en MongoDB.

        Guardamos el documento insertado para verificar después qué intentó
        guardar el endpoint.
        """
        self.documento_insertado = documento
        return ResultadoInsertOneFalso()


# =========================
# PRUEBAS DE VALIDACIONES
# =========================

def test_validar_medicamento_exitoso():
    """
    CASO VÁLIDO: todos los campos cumplen las reglas.

    validar_medicamento debe devolver una lista vacía.
    """
    data = medicamento_valido()

    errores = validar_medicamento(data)

    assert errores == []


def test_nombre_medicamento_vacio():
    """
    CASO INVÁLIDO: nombre_medicamento vacío.
    """
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    errores = validar_medicamento(data)

    assert "El nombre del medicamento es obligatorio" in errores


def test_dosis_vacia():
    """
    CASO INVÁLIDO: dosis_cantidad vacía.
    """
    data = medicamento_valido()
    data["dosis_cantidad"] = ""

    errores = validar_medicamento(data)

    assert "La dosis es obligatoria" in errores


def test_frecuencia_vacia():
    """
    CASO INVÁLIDO: frecuencia vacía.
    """
    data = medicamento_valido()
    data["frecuencia"] = ""

    errores = validar_medicamento(data)

    assert "La frecuencia es obligatoria" in errores


def test_horario_vacio():
    """
    CASO INVÁLIDO: lista de horarios vacía.
    """
    data = medicamento_valido()
    data["horarios"] = []

    errores = validar_medicamento(data)

    assert "Debe ingresar al menos un horario" in errores


def test_fecha_inicio_vacia():
    """
    CASO INVÁLIDO: fecha_inicio vacía.
    """
    data = medicamento_valido()
    data["fecha_inicio"] = ""

    errores = validar_medicamento(data)

    assert "La fecha de inicio es obligatoria" in errores


def test_paciente_id_faltante():
    """
    CASO INVÁLIDO: falta paciente_id.

    paciente_id es obligatorio porque el medicamento debe quedar asociado
    a un paciente.
    """
    data = medicamento_valido()
    del data["paciente_id"]

    errores = validar_medicamento(data)

    assert "El paciente_id es obligatorio" in errores


def test_paciente_id_invalido_texto():
    """
    CASO INVÁLIDO: paciente_id no es ObjectId.

    Antes se validaba como entero. Después de la migración a MongoDB,
    debe ser un ObjectId válido.
    """
    data = medicamento_valido()
    data["paciente_id"] = "abc"

    errores = validar_medicamento(data)

    assert "El paciente_id debe ser un ObjectId válido" in errores


def test_paciente_id_invalido_menor_o_igual_a_cero():
    """
    CASO INVÁLIDO: paciente_id numérico viejo.

    Esta prueba confirma que los IDs enteros ya no son válidos para esta ruta,
    porque ahora se trabaja con ObjectId de MongoDB.
    """
    data = medicamento_valido()
    data["paciente_id"] = 0

    errores = validar_medicamento(data)

    assert "El paciente_id debe ser un ObjectId válido" in errores


# =========================
# PRUEBAS DE BASE DE DATOS LEGADAS
# =========================

def test_verificar_paciente_existe_devuelve_true():
    """
    Prueba unitaria de verificar_paciente_existe con SQLite en memoria.

    Aunque medication_route.py ya fue migrado a MongoDB, esta función sigue
    existiendo en validaciones.py. Se conserva esta prueba porque valida
    su comportamiento aislado.
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
        "Ana", "Lopez", "01/15/1990", "Femenino",
        "CC", "12345678", "3001234567", "Sura", "Hipertension"
    ))

    conn.commit()

    resultado = verificar_paciente_existe(1, conn)

    assert resultado is True
    conn.close()


def test_verificar_paciente_existe_devuelve_false():
    """
    Prueba unitaria de verificar_paciente_existe cuando no hay paciente.
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

    resultado = verificar_paciente_existe(99, conn)

    assert resultado is False
    conn.close()


def test_verificar_medicamento_duplicado_devuelve_true():
    """
    Prueba unitaria de verificar_medicamento_duplicado con SQLite en memoria.

    Se conserva porque la función sigue existiendo en validaciones.py.
    """
    conn = sqlite3.connect(":memory:")
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

    cursor.execute("""
        INSERT INTO medicamentos (
            nombre, dosis, frecuencia, horario,
            fecha_inicio, observaciones, paciente_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Acetaminofen", "1 tableta", "Cada 8 horas", "08:00, 16:00, 00:00",
        "03/16/2026", "Concentración: 500 mg | Forma farmacéutica: Tableta", 1
    ))

    conn.commit()

    resultado = verificar_medicamento_duplicado("Acetaminofen", 1, conn)

    assert resultado is True
    conn.close()


def test_verificar_medicamento_duplicado_devuelve_false():
    """
    Prueba unitaria de verificar_medicamento_duplicado cuando no existe
    medicamento duplicado.
    """
    conn = sqlite3.connect(":memory:")
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

    resultado = verificar_medicamento_duplicado("Ibuprofeno", 1, conn)

    assert resultado is False
    conn.close()


# =========================
# PRUEBAS DEL ENDPOINT
# =========================

def test_post_medicamento_exitoso(monkeypatch):
    """
    CASO VÁLIDO DEL ENDPOINT POST /medicamentos/.

    La ruta actual ya no usa SQLite. Ahora:
    1. Valida el body.
    2. Busca el paciente en pacientes_col usando ObjectId.
    3. Verifica duplicado en medicamentos_col.
    4. Inserta el medicamento en medicamentos_col.
    5. Retorna el id creado.

    Por eso se mockean pacientes_col y medicamentos_col, no sqlite3.
    """
    data = medicamento_valido()

    pacientes_col_falsa = PacientesColFalsa(
        paciente_existente={
            "_id": PACIENTE_ID_VALIDO,
            "nombres": "Juan"
        }
    )

    medicamentos_col_falsa = MedicamentosColFalsa(
        medicamento_existente=None
    )

    monkeypatch.setattr(
        "backend.routes.medication_route.pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.medication_route.medicamentos_col",
        medicamentos_col_falsa
    )

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Medicamento registrado exitosamente"
    assert response.json()["medicamento_id"] == "medicamento-test-id"

    documento = medicamentos_col_falsa.documento_insertado

    assert documento is not None
    assert documento["nombre"] == "acetaminofen"
    assert documento["dosis"] == "1 tableta"
    assert documento["frecuencia"] == "Cada 8 horas"
    assert documento["horario"] == "08:00, 16:00, 00:00"
    assert documento["fecha_inicio"] == "03/16/2026"
    assert documento["paciente_id"] == PACIENTE_ID_VALIDO


def test_post_medicamento_datos_invalidos():
    """
    CASO INVÁLIDO DEL ENDPOINT POST /medicamentos/.

    Enviamos token válido para que el middleware permita llegar al endpoint.
    Luego la validación debe fallar porque nombre_medicamento está vacío.
    """
    data = medicamento_valido()
    data["nombre_medicamento"] = ""

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert "El nombre del medicamento es obligatorio" in response.json()["detail"]


def test_post_medicamento_paciente_no_existe(monkeypatch):
    """
    CASO INVÁLIDO: el paciente asociado no existe.

    Simulamos que pacientes_col.find_one() devuelve None.
    La ruta debe responder 404.
    """
    data = medicamento_valido()

    pacientes_col_falsa = PacientesColFalsa(
        paciente_existente=None
    )

    monkeypatch.setattr(
        "backend.routes.medication_route.pacientes_col",
        pacientes_col_falsa
    )

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El paciente no existe"


def test_post_medicamento_duplicado(monkeypatch):
    """
    CASO INVÁLIDO: el paciente ya tiene registrado este medicamento.

    Simulamos que:
    - el paciente sí existe
    - medicamentos_col.find_one() encuentra un medicamento duplicado
    """
    data = medicamento_valido()

    pacientes_col_falsa = PacientesColFalsa(
        paciente_existente={
            "_id": PACIENTE_ID_VALIDO,
            "nombres": "Juan"
        }
    )

    medicamentos_col_falsa = MedicamentosColFalsa(
        medicamento_existente={
            "_id": "medicamento-existente-id",
            "paciente_id": PACIENTE_ID_VALIDO,
            "nombre": "acetaminofen"
        }
    )

    monkeypatch.setattr(
        "backend.routes.medication_route.pacientes_col",
        pacientes_col_falsa
    )

    monkeypatch.setattr(
        "backend.routes.medication_route.medicamentos_col",
        medicamentos_col_falsa
    )

    response = client.post(
        "/medicamentos/",
        json=data,
        headers=headers_auth()
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "El paciente ya tiene registrado este medicamento"