# Patrón Strategy

![Diagrama Strategy](./imagenes/strategy.png)

## Descripción
Este diagrama representa el patrón Strategy, el cual permite definir diferentes estrategias o comportamientos intercambiables para resolver una misma tarea dentro del sistema.

## Justificación
El patrón Strategy es coherente con la lógica del proyecto porque permite encapsular distintas formas de ejecutar una operación sin modificar la clase principal que las utiliza. Esto facilita la implementación de reglas, validaciones o procesos alternativos dentro del sistema, manteniendo una estructura más flexible y ordenada.

## Rol dentro del sistema
En este patrón, una clase cliente utiliza una estrategia según la necesidad del contexto. Esto permite cambiar comportamientos de forma dinámica, mejorar la reutilización de código y facilitar la extensión de nuevas estrategias en el futuro.
