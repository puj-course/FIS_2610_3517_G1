# Implementación del Patrón Decorator: Módulo de Historial de Tomas

![Patrón decorator](/docs/patrones/estructurales/imagenes/Patron%20decorator.png)

Este documento detalla el diseño y la implementación del patrón estructural **Decorator** aplicado al sistema de historial de tomas, destacando su arquitectura, componentes y beneficios en términos de escalabilidad.

## 1. Introducción al Patrón
El diagrama de clases modela la extensión dinámica del comportamiento del historial sin modificar su estructura original. Este enfoque garantiza el cumplimiento del principio **Abierto/Cerrado (Open/Closed Principle)**, permitiendo agregar funcionalidades sin alterar el código existente.

## 2. Componentes del Diseño

| Rol | Clase | Descripción |
| :--- | :--- | :--- |
| **Component** | `Historial` | Interfaz base que define el método `obtener_datos()`. Retorna la información en formato de diccionario. |
| **ConcreteComponent** | `HistorialBase` | Implementación básica que almacena y retorna las tomas crudas sin procesamiento adicional. |
| **Decorator** | `HistorialDecorator` | Clase abstracta que mantiene una referencia a un objeto `Historial` y delega la ejecución del método base. |
| **ConcreteDecorator A** | `CumplimientoDecorator` | Añade lógica para calcular porcentajes de cumplimiento y totales de registros realizados. |
| **ConcreteDecorator B** | `AlertasDecorator` | Genera mensajes informativos y alertas basadas en tomas con estado atrasado. |

## 3. Arquitectura y Relaciones
El diseño se fundamenta en dos pilares relacionales:
* **Herencia:** Tanto `HistorialBase` como `HistorialDecorator` implementan la interfaz `Historial`. Los decoradores concretos heredan de la clase abstracta decoradora.
* **Composición:** `HistorialDecorator` contiene un objeto de tipo `Historial`. Esta relación es clave, ya que permite envolver objetos de manera recursiva y construir cadenas de funcionalidades.

## 4. Flujo de Ejecución (Client)
El backend actúa como el cliente del patrón, gestionando la composición dinámica:
1. Se instancia el objeto real (`HistorialBase`).
2. Se "envuelve" (wrap) con los decoradores necesarios según el requerimiento (ej. Cumplimiento, luego Alertas).
3. El objeto resultante mantiene la misma interfaz, pero con comportamiento enriquecido.

## 5. Justificación y Ventajas
* **Responsabilidad Única:** `HistorialBase` solo se ocupa de los datos, mientras que los decoradores gestionan los cálculos y las alertas.
* **Mantenibilidad:** Evita el alto acoplamiento que produciría una implementación directa en la clase base.
* **Escalabilidad:** Para agregar nuevas métricas o análisis, no se modifican las clases existentes; simplemente se crean nuevos decoradores que se encadenan dinámicamente.

## 6. Conclusión
La aplicación del patrón **Decorator** en el historial de tomas proporciona una solución flexible y ordenada. Prepara al sistema para futuras ampliaciones de manera eficiente, garantizando que la evolución del software no comprometa la integridad del código previamente probado.