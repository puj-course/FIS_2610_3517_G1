# Patrón Observer

![Diagrama Observer](./imagenes/observer.png)

## Descripción
Este diagrama representa el patrón Observer, en el cual una clase principal actúa como sujeto y se encarga de notificar a distintos observadores cuando ocurre un cambio o evento relevante dentro del sistema.

## Justificación
El patrón Observer es coherente con la lógica del proyecto porque permite desacoplar la generación de eventos de las acciones que se ejecutan como respuesta. Esto resulta útil en procesos relacionados con alertas, recordatorios o notificaciones, donde varios componentes pueden reaccionar ante un mismo cambio sin depender directamente unos de otros.

## Rol dentro del sistema
En este patrón, el sujeto central administra los cambios de estado o eventos importantes y comunica dichas actualizaciones a los observadores registrados. De esta forma, el sistema gana flexibilidad y facilita la extensión de nuevas respuestas ante eventos futuros.
