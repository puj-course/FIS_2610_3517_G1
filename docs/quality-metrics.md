# Metricas de calidad de MedTrack

## Objetivo

MedTrack evalua metricas propias dentro del backend real y las muestra en el frontend real de la aplicacion. No se usa una app FastAPI separada ni un HTML aislado: la pantalla esta integrada en `/metricas-calidad` y consume los endpoints reales:

- `GET /metricas-calidad/resumen`
- `POST /metricas-calidad/evaluar`

Todas las metricas propias se expresan principalmente como porcentaje para que sean comparables entre si y para que el `quality_gate_aprobado` pueda decidirse con un umbral comun.

## Umbrales

| Rango | Nivel | Interpretacion |
| --- | --- | --- |
| 90% a 100% | Bueno | La metrica cumple el objetivo de calidad esperado. |
| 70% a 89% | Aceptable | La metrica funciona, pero hay riesgo o deuda a mejorar. |
| 0% a 69% | Deficiente | La metrica queda por debajo del minimo aceptado y bloquea el quality gate. |

El quality gate aprueba solo si las tres metricas estan en 70% o mas. Si una metrica queda deficiente, `quality_gate_aprobado` pasa a `false`.

## Metricas propias

### 1. Completitud de datos

**Que mide:** porcentaje de campos obligatorios completos en pacientes, medicamentos y recordatorios.

**Campos evaluados:**

| Entidad | Campos requeridos |
| --- | --- |
| Paciente | `paciente_id` o `id` o `_id`; `nombre`, `nombres`, `identificador` o `numero_documento` |
| Medicamento | `medicamento_id` o `id` o `_id`; `nombre`; `dosis`; `paciente_id` |
| Recordatorio | `recordatorio_id` o `id` o `_id`; `paciente_id`; `medicamento_id`; `hora_programada` o `hora_recordatorio`; `frecuencia` |

**Formula:**

```text
completitud = campos_completos / campos_totales * 100
```

**Que dato hace que cambie:** baja cuando un campo requerido queda vacio, en blanco, nulo o ausente. Por ejemplo, borrar `dosis` en un medicamento o `frecuencia` en un recordatorio reduce el porcentaje.

**Impacto:** datos incompletos afectan el seguimiento clinico porque impiden relacionar pacientes, medicamentos y recordatorios con suficiente informacion operativa.

**Acciones de mejora si falla:** reforzar validaciones de formularios, marcar campos obligatorios en frontend, rechazar registros incompletos en backend y agregar pruebas para cada entidad.

### 2. Cumplimiento de reglas de negocio

**Que mide:** porcentaje de reglas de coherencia cumplidas entre paciente, medicamento, recordatorio y toma.

**Reglas evaluadas:**

- Un medicamento debe estar asociado a un paciente existente.
- Un recordatorio debe estar asociado a un medicamento existente.
- Un recordatorio debe estar asociado a un paciente existente.
- El `paciente_id` del recordatorio debe coincidir con el `paciente_id` del medicamento.
- Una toma debe estar asociada a un paciente existente.
- Una toma debe estar asociada a un medicamento existente.
- Una toma debe estar asociada a un recordatorio existente cuando tenga `recordatorio_id`.
- La toma debe coincidir con la relacion paciente-medicamento.
- Si la toma tiene recordatorio, paciente y medicamento de la toma deben coincidir con los del recordatorio.

**Formula:**

```text
cumplimiento_reglas = reglas_cumplidas / reglas_totales * 100
```

**Que dato hace que cambie:** baja cuando se ingresan IDs inexistentes o relaciones incoherentes. Ejemplos: `paciente_id = "m1"` en un recordatorio, `medicamento_id = "0"` o una toma asociada a un paciente distinto al paciente del medicamento.

**Impacto:** esta metrica valida consistencia real del dominio. Un valor bajo indica que el sistema puede mostrar recordatorios o tomas asociadas a pacientes equivocados.

**Acciones de mejora si falla:** validar existencia de IDs antes de guardar, bloquear cambios que rompan relaciones, usar busquedas por `ObjectId` normalizadas y agregar pruebas de integridad para tomas y recordatorios.

### 3. Rendimiento / latencia

**Que mide:** porcentaje de cumplimiento del objetivo de rendimiento al calcular el reporte de metricas.

La latencia se mide internamente en milisegundos, pero en la app se muestra principalmente como porcentaje.

**Formula:**

```text
si latencia_ms <= objetivo_ms:
    porcentaje = 100
si latencia_ms > objetivo_ms:
    porcentaje = objetivo_ms / latencia_ms * 100
```

**Valor por defecto:** `objetivo_ms = 300`.

**Que dato hace que cambie:** baja si el calculo tarda mas que el objetivo. En pruebas manuales se puede enviar un `objetivo_ms` mas estricto o aumentar el volumen de datos del JSON.

**Impacto:** un porcentaje bajo indica que el calculo de calidad tarda demasiado para ser consultado desde la interfaz sin afectar la experiencia del usuario.

**Acciones de mejora si falla:** reducir consultas repetidas, indexar campos de relacion, limitar detalle cuando no se necesita y cachear reportes pesados.

## Respuesta del backend

Los endpoints devuelven este formato base:

```json
{
  "estado_general": "Aprobado",
  "quality_gate_aprobado": true,
  "notificacion": {
    "tipo": "APROBADO",
    "mensaje": "Todas las metricas propias cumplen el umbral minimo de calidad.",
    "metricas_afectadas": []
  },
  "resumen_metricas": {
    "completitud_datos": {
      "porcentaje": 100.0,
      "nivel": "Bueno",
      "lectura": "100.0% - Bueno"
    },
    "cumplimiento_reglas_negocio": {
      "porcentaje": 100.0,
      "nivel": "Bueno",
      "lectura": "100.0% - Bueno"
    },
    "rendimiento_latencia": {
      "porcentaje": 100.0,
      "nivel": "Bueno",
      "lectura": "100.0% - Bueno",
      "latencia_ms": 0.01,
      "objetivo_ms": 300
    }
  }
}
```

## Como probar desde la app

1. Iniciar backend y frontend.
2. Iniciar sesion en MedTrack.
3. Abrir `/metricas-calidad`.
4. Presionar `Evaluar datos actuales del sistema` para leer MongoDB.
5. Presionar `Cargar escenario valido` y luego `Evaluar JSON`. Debe aprobar.
6. Presionar `Cargar escenario con dato incorrecto` y luego `Evaluar JSON`. Debe fallar por reglas de negocio.

Cambios manuales para demostrar cada metrica:

- Completitud: dejar `dosis`, `frecuencia` o `hora_programada` como cadena vacia.
- Reglas de negocio: cambiar `recordatorios[0].paciente_id` a `"m1"` o `recordatorios[0].medicamento_id` a `"0"`.
- Rendimiento: bajar `objetivo_ms` a un valor muy pequeno o aumentar fuertemente el volumen del JSON.

## Como probar con tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v tests/test_quality_metrics.py tests/test_quality_metrics_route.py
```

Los tests validan:

- Escenario valido con 100% en las tres metricas.
- Escenario invalido por campos faltantes.
- Escenario invalido por IDs incoherentes.
- Cambio de porcentaje cuando cambia un dato.
- Latencia con porcentaje, `latencia_ms`, `objetivo_ms` y nivel.
- Endpoints `GET /resumen` y `POST /evaluar`.

## Como probar con escenarios versionados

```powershell
.\.venv\Scripts\python.exe scripts\run_quality_metrics_scenarios.py
```

El script lee:

- `data/quality/quality_metrics_valid.json`
- `data/quality/quality_metrics_invalid.json`

Y genera:

- `reports/quality/quality_metrics_valid_result.json`
- `reports/quality/quality_metrics_invalid_result.json`
- `reports/quality/quality_metrics_summary.md`

El script falla si el escenario valido no aprueba, si el escenario invalido no falla o si alguna metrica no trae porcentaje.

## Pipeline

El workflow dedicado esta en:

```text
.github/workflows/quality-metrics.yml
```

Ejecuta:

- Validacion de sintaxis de `backend/quality_metrics.py` y `backend/routes/quality_metrics_route.py`.
- Tests con cobertura enfocada en las metricas.
- Script de escenarios versionados.
- Build del frontend React/Vite.
- Publicacion de artifacts con reportes JSON y `coverage-quality-metrics.xml`.
- Resumen de GitHub Actions con porcentajes, estado de escenarios, ruta frontend y endpoints.

## Relacion con SonarQube

Estas metricas son distintas a SonarQube porque evalúan datos y coherencia del dominio MedTrack en tiempo de ejecucion. SonarQube sigue midiendo calidad estatica como coverage, duplicacion, seguridad, confiabilidad y mantenibilidad.
