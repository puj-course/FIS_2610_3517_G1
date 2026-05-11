# tests/test_validar_medicamento.py
# Pruebas funcionales para validar_medicamento()

from backend.validaciones import validar_medicamento


# ObjectId válido de prueba.
# Después de la migración a MongoDB, paciente_id ya no debe ser un entero.
# Debe ser un string con formato ObjectId válido.
PACIENTE_ID_VALIDO = "507f1f77bcf86cd799439011"


def medicamento_valido():
    """
    Datos base válidos para registrar un medicamento.

    Estos datos se reutilizan en varios tests. Si un caso necesita probar
    un error específico, modifica una copia de este diccionario.

    Nota importante:
    paciente_id debe ser un ObjectId válido porque la validación actual
    está alineada con MongoDB.
    """
    return {
        "nombre_medicamento": "Aspirina",
        "concentracion": "500 mg",
        "forma_farmaceutica": "Tableta",
        "dosis_cantidad": 1,
        "dosis_unidad": "tableta",
        "frecuencia": "Cada 8 horas",
        "fecha_inicio": "03/14/2026",
        "paciente_id": PACIENTE_ID_VALIDO,
        "horarios": ["08:00", "14:00", "20:00"],
        "observaciones": "Tomar con agua",
    }


class TestCasosValidos:
    """
    Casos donde validar_medicamento() debe devolver lista vacía.

    Si alguno de estos tests falla con:
    'El paciente_id debe ser un ObjectId válido',
    significa que se volvió a usar un paciente_id entero o inválido.
    """

    def test_registro_completo_sin_errores(self):
        errores = validar_medicamento(medicamento_valido())
        assert errores == []

    def test_observaciones_opcionales_pueden_omitirse(self):
        data = medicamento_valido()
        del data["observaciones"]

        assert validar_medicamento(data) == []

    def test_observaciones_vacias_son_validas(self):
        data = medicamento_valido()
        data["observaciones"] = ""

        assert validar_medicamento(data) == []

    def test_fecha_inicio_en_2026_es_valida(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "03/14/2026"

        assert validar_medicamento(data) == []


class TestCamposVacios:
    """
    Casos donde campos obligatorios llegan vacíos.

    La función debe reportar el mensaje correspondiente para cada campo.
    """

    def test_nombre_vacio(self):
        data = medicamento_valido()
        data["nombre_medicamento"] = ""

        errores = validar_medicamento(data)

        assert "El nombre del medicamento es obligatorio" in errores

    def test_concentracion_vacia(self):
        data = medicamento_valido()
        data["concentracion"] = ""

        errores = validar_medicamento(data)

        assert "La concentración es obligatoria" in errores

    def test_forma_farmaceutica_vacia(self):
        data = medicamento_valido()
        data["forma_farmaceutica"] = ""

        errores = validar_medicamento(data)

        assert "La forma farmacéutica es obligatoria" in errores

    def test_dosis_vacia(self):
        data = medicamento_valido()
        data["dosis_cantidad"] = ""

        errores = validar_medicamento(data)

        assert "La dosis es obligatoria" in errores

    def test_unidad_dosis_vacia(self):
        data = medicamento_valido()
        data["dosis_unidad"] = ""

        errores = validar_medicamento(data)

        assert "La unidad de la dosis es obligatoria" in errores

    def test_frecuencia_vacia(self):
        data = medicamento_valido()
        data["frecuencia"] = ""

        errores = validar_medicamento(data)

        assert "La frecuencia es obligatoria" in errores

    def test_horarios_vacios(self):
        data = medicamento_valido()
        data["horarios"] = []

        errores = validar_medicamento(data)

        assert "Debe ingresar al menos un horario" in errores

    def test_fecha_inicio_vacia(self):
        data = medicamento_valido()
        data["fecha_inicio"] = ""

        errores = validar_medicamento(data)

        assert "La fecha de inicio es obligatoria" in errores

    def test_paciente_id_vacio(self):
        """
        Caso inválido: paciente_id vacío.

        Aunque MongoDB usa ObjectId, el campo sigue siendo obligatorio.
        """
        data = medicamento_valido()
        data["paciente_id"] = ""

        errores = validar_medicamento(data)

        assert "El paciente_id es obligatorio" in errores

    def test_todos_los_obligatorios_vacios_generan_multiples_errores(self):
        """
        Caso extremo: todos los campos obligatorios vacíos.

        Deben generarse múltiples errores de validación.
        """
        data = {
            "nombre_medicamento": "",
            "concentracion": "",
            "forma_farmaceutica": "",
            "dosis_cantidad": "",
            "dosis_unidad": "",
            "frecuencia": "",
            "fecha_inicio": "",
            "paciente_id": "",
            "horarios": []
        }

        errores = validar_medicamento(data)

        assert len(errores) >= 8


class TestFormatoFecha:
    """
    Casos donde fecha_inicio tiene formato incorrecto.

    El formato válido esperado por el proyecto es mm/dd/yyyy.
    """

    def test_formato_ddmmyyyy_es_incorrecto(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "14/03/2026"

        errores = validar_medicamento(data)

        assert any("fecha" in e.lower() for e in errores)

    def test_fecha_sin_separadores_es_incorrecta(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "03142026"

        errores = validar_medicamento(data)

        assert any("fecha" in e.lower() for e in errores)

    def test_texto_no_es_fecha_valida(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "no-es-una-fecha"

        errores = validar_medicamento(data)

        assert any("fecha" in e.lower() for e in errores)


class TestNombreCorto:
    """
    Casos relacionados con el formato del nombre del medicamento.
    """

    def test_nombre_de_un_caracter_es_invalido(self):
        data = medicamento_valido()
        data["nombre_medicamento"] = "A"

        errores = validar_medicamento(data)

        assert any("nombre" in e.lower() or "2 caracteres" in e.lower() for e in errores)


class TestPacienteId:
    """
    Casos inválidos para paciente_id.

    Antes se probaban enteros negativos, cero o texto porque SQLite usaba IDs
    numéricos. Después de la migración a MongoDB, el criterio correcto es que
    paciente_id sea un string con formato ObjectId válido.
    """

    def test_paciente_id_cero_es_invalido(self):
        data = medicamento_valido()
        data["paciente_id"] = 0

        errores = validar_medicamento(data)

        assert "El paciente_id debe ser un ObjectId válido" in errores

    def test_paciente_id_negativo_es_invalido(self):
        data = medicamento_valido()
        data["paciente_id"] = -1

        errores = validar_medicamento(data)

        assert "El paciente_id debe ser un ObjectId válido" in errores

    def test_paciente_id_como_texto_no_objectid_es_invalido(self):
        data = medicamento_valido()
        data["paciente_id"] = "abc"

        errores = validar_medicamento(data)

        assert "El paciente_id debe ser un ObjectId válido" in errores

    def test_paciente_id_con_formato_invalido(self):
        data = medicamento_valido()
        data["paciente_id"] = "123456"

        errores = validar_medicamento(data)

        assert "El paciente_id debe ser un ObjectId válido" in errores

    def test_paciente_id_con_formato_objectid_es_valido(self):
        data = medicamento_valido()
        data["paciente_id"] = PACIENTE_ID_VALIDO

        errores = validar_medicamento(data)

        assert errores == []
