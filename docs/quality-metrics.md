# Métricas de calidad del backend MedTrack

## 1. Objetivo

Este documento presenta las métricas de calidad usadas para evaluar el backend de MedTrack.

Se diferencian dos gruposs:

1. Métricas automáticas de SonarQube/SonarCloud.
2. Métricas propias implementadas por el equipo.

SonarQube mide calidad estática del código, como cobertura, duplicación, mantenibilidad, confiabilidad y seguridad. Las métricas propias evalúan aspectos funcionales del dominio de MedTrack que SonarQube no mide directamente.

---

## 2. Métricas de SonarQube

### 2.1 Coverage

**Qué mide:**  
Mide el porcentaje de líneas de código ejecutadas por las pruebas automatizadas.

**Interpretación:**  
Un coverage mayor o igual al 80% indica que una parte significativa del backend está cubierta por pruebas automatizadas.

**Impacto en la calidad:**  
Reduce el riesgo de introducir errores al modificar rutas, servicios o validaciones.

**Acciones de mejora:**  
Mantener pruebas para nuevas rutas, servicios, validaciones y casos de error.

---

### 2.2 Duplications

**Qué mide:**  
Mide el porcentaje de código duplicado dentro del proyecto.

**Interpretación:**  
Un porcentaje bajo de duplicación indica que el backend evita repetir lógica innecesaria.

**Impacto en la calidad:**  
Mejora la mantenibilidad, la reutilización y la facilidad de cambio.

**Acciones de mejora:**  
Extraer lógica repetida a funciones auxiliares, servicios o utilidades compartidas.

---

### 2.3 Reliability

**Qué mide:**  
Evalúa posibles bugs o problemas que pueden afectar el comportamiento correcto del sistema.

**Interpretación:**  
Una calificación A indica que no existen problemas críticos de confiabilidad en el código nuevo analizado.

**Impacto en la calidad:**  
Aumenta la estabilidad del backend y reduce errores en ejecución.

**Acciones de mejora:**  
Evitar excepciones genéricas, validar entradas y mantener pruebas para escenarios de error.

---

### 2.4 Maintainability

**Qué mide:**  
Evalúa la facilidad de mantener, modificar y comprender el código.

**Interpretación:**  
Una calificación A indica que el código tiene una estructura mantenible.

**Impacto en la calidad:**  
Facilita que el equipo evolucione el sistema sin introducir deuda técnica excesiva.

**Acciones de mejora:**  
Mantener funciones pequeñas, reducir complejidad cognitiva y separar responsabilidades.

---

## 3. Métricas propias implementadas

### 3.1 Completitud de datos

**Qué mide:**  
Mide qué porcentaje de campos importantes está completo en pacientes, medicamentos y recordatorios.

**Cómo se calcula:**

```text
completitud = campos completos / campos totales * 100
