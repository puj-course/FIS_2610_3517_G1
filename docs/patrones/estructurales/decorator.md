# Implementación del Patrón Decorator: Módulo de Historial de Tomas

![Patron decorator](/docs/patrones/estructurales/imagenes/PatronDecorator%20final.png)

Este documento detalla el diseño y la implementación del patrón estructural **Decorator** aplicado al sistema de historial de tomas, destacando su arquitectura, componentes y beneficios en términos de escalabilidad.

## 1. Introducción al Patrón
El diagrama de clases modela la extensión dinámica del comportamiento del historial sin modificar su estructura original. Este enfoque garantiza el cumplimiento del principio **Abierto/Cerrado (Open/Closed Principle)**, permitiendo agregar funcionalidades sin alterar el código existente.

## 2. Diagrama de Clases y Estructura
El diseño se organiza en una jerarquía que separa las responsabilidades de obtención de datos, decoración base y lógica de negocio específica.

### **2.1. Componentes del Patrón**

#### **A. Interfaz Base (`Component`): `Historial`**
Es el contrato que define la estructura de salida.
- **Método:** `obtener_datos() -> dict`
- **Función:** Establece que cualquier objeto (ya sea base o decorado) debe retornar un diccionario con la información del historial, permitiendo el polimorfismo.

#### **B. Componente Concreto (`ConcreteComponent`): `HistorialTomas`**
Representa la funcionalidad básica del sistema.
- **Responsabilidad:** Recibe las tomas crudas desde la base de datos a través del backend.
- **Estado:** Es el objeto "envuelto" original que carece de lógica de cálculo o alertas.

#### **C. Decorador Abstracto (`Decorator`): `HistorialDecorator`**
Clase base para todas las extensiones.
- **Composición:** Mantiene una referencia a un objeto de tipo `Historial`.
- **Delegación:** Implementa `obtener_datos()` delegando la llamada al objeto interno, sirviendo como plantilla para añadir comportamiento adicional.



## 3. Extensiones Especializadas (Decoradores Concretos)

El sistema implementa dos capas de lógica adicional que se activan según la necesidad del cliente:

### **3.1. CumplimientoDecorator**
Añade una capa analítica sobre el historial.
- **Lógica:** Calcula el total de registros y el número de tomas marcadas como "realizadas".
- **Salida:** Genera un porcentaje de cumplimiento que se integra en el JSON final.

### **3.2. AlertasDecorator**
Añade una capa de monitoreo y notificación.
- **Lógica:** Escanea el historial en busca de registros con estados de error o retraso.
- **Salida:** Inyecta un arreglo de cadenas de texto con mensajes de advertencia para el usuario final.

---

## 4. Implementación del Flujo en el Backend (`TomaRoute`)

La clase `TomaRoute` actúa como el controlador en el framework **FastAPI**, encargándose de la orquestación de los objetos. 

**Proceso de construcción dinámica:**
1.  **Carga de Datos:** Recupera los modelos de la base de datos.
2.  **Inicialización:** Instancia el `HistorialTomas` (Componente Concreto).
3.  **Encadenamiento (Wrapping):**
    - Se envuelve con `CumplimientoDecorator` para calcular estadísticas.
    - El resultado se envuelve con `AlertasDecorator` para procesar notificaciones.
4.  **Ejecución:** Se llama a `obtener_datos()` en el decorador más externo, lo que dispara una ejecución en cadena hacia el objeto base.

---

## 5. Justificación de Ingeniería de Software

El uso de este patrón se justifica por los siguientes principios:

| Principio | Aplicación en el Proyecto |
| :--- | :--- |
| **Open/Closed Principle** | El sistema es **abierto** a nuevas métricas (ej. nuevas clases de estadísticas) pero **cerrado** a la modificación de `HistorialTomas`. |
| **Single Responsibility** | `HistorialTomas` solo maneja datos; `CumplimientoDecorator` solo maneja cálculos; `AlertasDecorator` solo maneja mensajes. |
| **Composición sobre Herencia** | Evita la creación de una explosión de subclases (ej. `HistorialConAlertas`, `HistorialConMetricasYAlertas`, etc.). |
| **Flexibilidad Dinámica** | La composición ocurre en tiempo de ejecución, permitiendo que el backend decida qué decoradores aplicar según el rol del usuario o el tipo de consulta. |

---

## 6. Conclusión
La implementación del patrón **Decorator** dota al módulo de historial de una flexibilidad superior. Esta arquitectura no solo resuelve los requerimientos actuales de alertas y cumplimiento, sino que establece una base sólida para futuras integraciones (como exportación a PDF, análisis predictivo o auditoría de cambios) sin poner en riesgo la estabilidad del código existente.