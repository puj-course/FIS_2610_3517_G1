
# Patrón Decorator

![Diagrama Decorator](./imagenes/decorator.png)

## Descripción
Este diagrama representa la implementación del patrón de diseño estructural **Decorator** aplicada al módulo de historial de tomas del sistema. Su propósito es permitir la extensión dinámica del comportamiento de un objeto sin modificar su estructura original, favoreciendo un diseño flexible, mantenible y escalable.

## Justificación
El uso del patrón Decorator en este módulo se justifica por la necesidad de agregar funcionalidades adicionales al historial de tomas sin alterar la clase base. En lugar de concentrar toda la lógica en una sola clase rígida, el sistema permite incorporar nuevos comportamientos mediante decoradores que se encadenan dinámicamente. Esto facilita la evolución del sistema y respeta el principio de abierto/cerrado, ya que las clases existentes no necesitan modificarse para extender la funcionalidad.

## Estructura del patrón en el sistema

### Componente base
La clase `Historial` actúa como la interfaz base del patrón. Define el contrato común que deben cumplir todas las clases relacionadas mediante el método `obtener_datos()`, el cual retorna la información del historial en formato diccionario. Esta abstracción permite tratar de manera uniforme tanto la implementación base como los decoradores.

### Componente concreto
`HistorialBase` corresponde al componente concreto. Su responsabilidad es almacenar y retornar las tomas del historial sin procesamiento adicional. Esta clase maneja los datos originales del sistema y los expone directamente, sin incluir cálculos ni generación de alertas.

### Decorador abstracto
La clase `HistorialDecorator` implementa igualmente la interfaz `Historial` y mantiene una referencia a otro objeto de este mismo tipo. Su función es envolver dicho objeto y delegar la ejecución del método `obtener_datos()`. Esta estructura basada en composición permite que las subclases añadan comportamiento sin modificar la implementación original.

### Decoradores concretos
A partir del decorador abstracto se derivan los decoradores concretos:

- `CumplimientoDecorator`: agrega información relacionada con el porcentaje de cumplimiento de las tomas, calculando el total de registros, cuántos han sido realizados y el porcentaje correspondiente.
- `AlertasDecorator`: genera alertas a partir de las tomas que se encuentran en estado atrasado, construyendo mensajes informativos para el usuario.

Ambos decoradores enriquecen la información original sin alterar la estructura base del historial.

## Cliente del patrón
El cliente del patrón está representado por el flujo del backend, el cual construye dinámicamente la composición de objetos. Primero se instancia un objeto de tipo `HistorialBase` y posteriormente se envuelve con los decoradores necesarios según los requerimientos del sistema. Esto permite combinar funcionalidades sin modificar las clases ya existentes.

## Relaciones principales
El diagrama evidencia tanto relaciones de herencia como de composición:

- `HistorialBase` implementa la interfaz `Historial`.
- `HistorialDecorator` también implementa `Historial`.
- Los decoradores concretos heredan de `HistorialDecorator`.
- `HistorialDecorator` mantiene una relación de composición con `Historial`, lo que permite envolver objetos de forma recursiva.

## Beneficios en el proyecto
La implementación de este patrón aporta varias ventajas al sistema:

- permite extender el comportamiento del historial sin modificar su clase base;
- facilita la combinación de múltiples funcionalidades sobre un mismo objeto;
- mejora la mantenibilidad y escalabilidad;
- reduce el acoplamiento entre responsabilidades;
- favorece un diseño modular y reutilizable.

## Conclusión
El patrón Decorator resulta adecuado para este módulo porque permite enriquecer progresivamente la información del historial de tomas mediante componentes independientes y combinables. De esta forma, el sistema puede crecer sin comprometer la claridad del diseño ni la estabilidad de las clases existentes.
