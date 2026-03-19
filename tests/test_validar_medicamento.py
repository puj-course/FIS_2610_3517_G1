# tests/test_validar_medicamento.py
# Pruebas funcionales para validar_medicamento() — issue #197
# Cubre casos válidos e inválidos según los criterios de aceptación.
#
# Ejecutar con:   pytest tests/test_validar_medicamento.py -v

import pytest
from backend.validaciones import validar_medicamento


# ── Dato base válido ──────────────────────────────────────────────────────────

def medicamento_valido():
    """Devuelve un diccionario con todos los campos correctos."""
    return {
        "nombre":        "Aspirina",
        "dosis":         "500mg",
        "frecuencia":    "Cada 8 horas",
        "horario":       "08:00, 14:00, 20:00",
        "fecha_inicio":  "03/14/2026",
        "paciente_id":   1,
        "observaciones": "Tomar con agua",
    }


# ── CASOS VÁLIDOS ─────────────────────────────────────────────────────────────

class TestCasosValidos:
    """El medicamento debe registrarse sin errores cuando los datos son correctos."""

    def test_registro_completo_sin_errores(self):
        """Todos los campos obligatorios completos y correctos → sin errores."""
        errores = validar_medicamento(medicamento_valido())
        assert errores == [], f"No se esperaban errores, pero se obtuvieron: {errores}"

    def test_observaciones_opcionales_pueden_omitirse(self):
        """El campo observaciones es opcional; omitirlo no genera error."""
        data = medicamento_valido()
        del data["observaciones"]
        assert validar_medicamento(data) == []

    def test_observaciones_vacias_son_validas(self):
        """Observaciones en blanco también se aceptan."""
        data = medicamento_valido()
        data["observaciones"] = ""
        assert validar_medicamento(data) == []

    def test_todas_las_frecuencias_validas_son_aceptadas(self):
        """Cada frecuencia permitida debe pasar sin errores."""
        frecuencias = [
            "Cada 4 horas", "Cada 6 horas", "Cada 8 horas", "Cada 12 horas",
            "Cada 24 horas", "Una vez al día", "Dos veces al día", "Tres veces al día"
        ]
        for f in frecuencias:
            data = medicamento_valido()
            data["frecuencia"] = f
            errores = validar_medicamento(data)
            assert errores == [], f"Frecuencia '{f}' debería ser válida pero generó: {errores}"

    def test_fecha_inicio_en_2026_es_valida(self):
        """Una fecha actual (2026) debe ser aceptada."""
        data = medicamento_valido()
        data["fecha_inicio"] = "03/14/2026"
        assert validar_medicamento(data) == []


# ── CASOS INVÁLIDOS: campos vacíos ───────────────────────────────────────────

class TestCamposVacios:
    """Los campos obligatorios vacíos deben generar error."""

    def test_nombre_vacio(self):
        data = medicamento_valido()
        data["nombre"] = ""
        errores = validar_medicamento(data)
        assert any("nombre" in e.lower() for e in errores)

    def test_dosis_vacia(self):
        data = medicamento_valido()
        data["dosis"] = ""
        errores = validar_medicamento(data)
        assert any("dosis" in e.lower() for e in errores)

    def test_frecuencia_vacia(self):
        data = medicamento_valido()
        data["frecuencia"] = ""
        errores = validar_medicamento(data)
        assert any("frecuencia" in e.lower() for e in errores)

    def test_horario_vacio(self):
        data = medicamento_valido()
        data["horario"] = ""
        errores = validar_medicamento(data)
        assert any("horario" in e.lower() for e in errores)

    def test_fecha_inicio_vacia(self):
        data = medicamento_valido()
        data["fecha_inicio"] = ""
        errores = validar_medicamento(data)
        assert any("fecha" in e.lower() for e in errores)

    def test_paciente_id_cero(self):
        data = medicamento_valido()
        data["paciente_id"] = 0
        errores = validar_medicamento(data)
        assert any("paciente" in e.lower() for e in errores)

    def test_todos_los_obligatorios_vacios_generan_multiples_errores(self):
        """Con todos los campos vacíos deben aparecer al menos 6 errores."""
        data = {
            "nombre": "", "dosis": "", "frecuencia": "",
            "horario": "", "fecha_inicio": "", "paciente_id": 0
        }
        errores = validar_medicamento(data)
        assert len(errores) >= 6, f"Se esperaban ≥6 errores, se obtuvieron {len(errores)}"


# ── CASOS INVÁLIDOS: formato de fecha ────────────────────────────────────────

class TestFormatoFecha:
    """La fecha de inicio debe tener formato mm/dd/yyyy."""

    def test_formato_ddmmyyyy_es_incorrecto(self):
        """El formato dd/mm/yyyy no es aceptado."""
        data = medicamento_valido()
        data["fecha_inicio"] = "14/03/2026"
        errores = validar_medicamento(data)
        assert any("fecha" in e.lower() for e in errores)

    def test_fecha_sin_separadores_es_incorrecta(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "03142026"
        errores = validar_medicamento(data)
        assert any("fecha" in e.lower() for e in errores)

    def test_fecha_anterior_a_2000_es_invalida(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "01/01/1999"
        errores = validar_medicamento(data)
        assert any("2000" in e or "fecha" in e.lower() for e in errores)

    def test_texto_no_es_fecha_valida(self):
        data = medicamento_valido()
        data["fecha_inicio"] = "no-es-una-fecha"
        errores = validar_medicamento(data)
        assert any("fecha" in e.lower() for e in errores)


# ── CASOS INVÁLIDOS: frecuencia ───────────────────────────────────────────────

class TestFrecuenciaInvalida:
    """La frecuencia debe ser exactamente una de las opciones permitidas."""

    def test_frecuencia_no_permitida(self):
        data = medicamento_valido()
        data["frecuencia"] = "Cada 3 horas"
        errores = validar_medicamento(data)
        assert any("frecuencia" in e.lower() for e in errores)

    def test_frecuencia_en_mayusculas_no_es_valida(self):
        """La comparación es sensible a mayúsculas/minúsculas."""
        data = medicamento_valido()
        data["frecuencia"] = "CADA 8 HORAS"
        errores = validar_medicamento(data)
        assert any("frecuencia" in e.lower() for e in errores)


# ── CASOS INVÁLIDOS: nombre muy corto ────────────────────────────────────────

class TestNombreCorto:

    def test_nombre_de_un_caracter_es_invalido(self):
        data = medicamento_valido()
        data["nombre"] = "A"
        errores = validar_medicamento(data)
        assert any("nombre" in e.lower() or "2 car" in e.lower() for e in errores)


# ── CASOS INVÁLIDOS: paciente_id ─────────────────────────────────────────────

class TestPacienteId:

    def test_paciente_id_negativo(self):
        data = medicamento_valido()
        data["paciente_id"] = -1
        errores = validar_medicamento(data)
        assert any("paciente" in e.lower() for e in errores)

    def test_paciente_id_como_texto(self):
        data = medicamento_valido()
        data["paciente_id"] = "abc"
        errores = validar_medicamento(data)
        assert any("paciente" in e.lower() for e in errores)
