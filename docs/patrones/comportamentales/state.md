# Patrón State

![Diagrama State](./imagenes/state.png)

## Descripción
Este diagrama representa la implementación del patrón de diseño comportamental **State** aplicado al manejo del estado de una toma de medicamento. Su propósito es permitir que un objeto cambie su comportamiento según su estado interno, evitando el uso excesivo de condicionales dispersos en el sistema.

## Justificación
El patrón State se utiliza porque el sistema necesita representar distintos comportamientos para una toma de medicamento dependiendo de su situación actual. En este caso, una toma puede encontrarse en estado pendiente, tomada o atrasada. En lugar de manejar todo con múltiples condiciones, cada estado se encapsula en una clase concreta, lo que mejora la claridad, el mantenimiento y la posibilidad de extender el sistema con nuevos estados.

## Estructura del patrón en el sistema

### Contexto
La función `calcular_estado()` actúa como contexto del patrón. Recibe la información del medicamento, la hora actual y las tomas registradas del día para decidir qué estado concreto debe instanciarse.

### Estado abstracto
La clase abstracta `EstadoToma` define la operación común:

- `obtener_estado(): str`

Esta operación obliga a todos los estados concretos a proporcionar una representación uniforme del estado actual.

### Estados concretos
A partir de `EstadoToma` se implementan los siguientes estados:

- `EstadoPendiente`
- `EstadoTomado`
- `EstadoAtrasado`

Cada uno encapsula su propia lógica y retorna el estado correspondiente.

## Reglas de transición observadas
Según el diseño mostrado en el diagrama, las reglas principales son:

- si el medicamento aparece registrado como tomado en las tomas del día, se instancia `EstadoTomado`;
- si la hora programada ya pasó y no existe registro oportuno, se instancia `EstadoAtrasado`;
- en cualquier otro caso, se instancia `EstadoPendiente`.

## Relaciones principales
El diagrama evidencia que:

- `calcular_estado()` utiliza e instancia objetos derivados de `EstadoToma`;
- `EstadoPendiente`, `EstadoTomado` y `EstadoAtrasado` heredan de la clase abstracta `EstadoToma`;
- cada estado implementa la operación `obtener_estado()`.

## Beneficios en el proyecto
- reduce el uso de condicionales repetidos;
- encapsula el comportamiento asociado a cada estado;
- mejora la claridad del diseño;
- facilita agregar nuevos estados en el futuro;
- favorece el mantenimiento y la extensión del sistema.

## Conclusión
El patrón State resulta adecuado para este módulo porque permite representar de manera clara y desacoplada los diferentes comportamientos asociados al estado de una toma de medicamento, manteniendo el sistema más ordenado y escalable.
