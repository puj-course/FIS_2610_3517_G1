# tests/test_validar_medicamento.py
# Pruebas funcionales para validar_medicamento()

from backend.validaciones import validar_medicamento


def medicamento_valido():
    return {
        "nombre_medicamento": "Aspirina",
        "concentracion": "500 mg",
        "forma_farmaceutica": "Tableta",
        "dosis_cantidad": 1,
        "dosis_unidad": "tableta",
        "frecuencia": "Cada 8 horas",
        "fecha_inicio": "03/14/2026",
        "paciente_id": 1,
        "horarios": ["08:00", "14:00", "20:00"],
        "observaciones": "Tomar con agua",
    }


class TestCasosValidos:
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

    def test_paciente_id_cero(self):
        data = medicamento_valido()
        data["paciente_id"] = 0
        errores = validar_medicamento(data)
        assert any("paciente_id" in e.lower() or "paciente" in e.lower() for e in errores)

    def test_todos_los_obligatorios_vacios_generan_multiples_errores(self):
        data = {
            "nombre_medicamento": "",
            "concentracion": "",
            "forma_farmaceutica": "",
            "dosis_cantidad": "",
            "dosis_unidad": "",
            "frecuencia": "",
            "fecha_inicio": "",
            "paciente_id": 0,
            "horarios": []
        }
        errores = validar_medicamento(data)
        assert len(errores) >= 8


class TestFormatoFecha:
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
    def test_nombre_de_un_caracter_es_invalido(self):
        data = medicamento_valido()
        data["nombre_medicamento"] = "A"
        errores = validar_medicamento(data)
        assert any("nombre" in e.lower() or "2 caracteres" in e.lower() for e in errores)


class TestPacienteId:
    def test_paciente_id_negativo(self):
        data = medicamento_valido()
        data["paciente_id"] = -1
        errores = validar_medicamento(data)
        assert any("paciente_id" in e.lower() or "paciente" in e.lower() for e in errores)

    def test_paciente_id_como_texto(self):
        data = medicamento_valido()
        data["paciente_id"] = "abc"
        errores = validar_medicamento(data)
        assert any("paciente_id" in e.lower() or "paciente" in e.lower() for e in errores)
