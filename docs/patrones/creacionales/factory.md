# Patrón Factory Method

![Diagrama Factory Method](./imagenes/factory-method.png)

## Descripción
Este diagrama representa la implementación del patrón de diseño creacional **Factory Method** en el proceso de creación de pacientes dentro del sistema. Su propósito es delegar la creación de objetos a clases especializadas, evitando que el cliente dependa directamente de la instanciación concreta.

## Justificación
El patrón Factory Method se utiliza porque el sistema necesita crear objetos de tipo paciente a partir de datos recibidos, manteniendo desacoplado al cliente de la clase concreta que finalmente se instancia. En lugar de que otras partes del sistema creen directamente un `PacienteGeneral`, la responsabilidad se delega a una fábrica concreta, haciendo el diseño más flexible y extensible.

## Estructura del patrón en el sistema

### Producto abstracto
La clase abstracta `Paciente` actúa como producto base del patrón. Define la estructura común que deben compartir los distintos tipos de paciente.

### Producto concreto
La clase `PacienteGeneral` corresponde al producto concreto. Representa una implementación específica de `Paciente` con atributos como:

- `nombre`
- `apellido`
- `fecha_nacimiento`
- `genero`
- `tipo_documento`
- `numero_documento`
- `telefono_contacto`
- `eps_aseguradora`
- `diagnostico_principal`
- `alergias_conocidas`
- `observaciones_adicionales`

Además, expone la operación:

- `como_tupla(): tuple`

### Creador abstracto
La clase abstracta `PacienteFactory` define el método de fábrica:

- `crear(data: dict): Paciente`

Este método establece el contrato para la creación de pacientes sin depender de una implementación concreta.

### Creador concreto
La clase `PacienteGeneralFactory` implementa el método de fábrica y se encarga de crear instancias de `PacienteGeneral`:

- `crear(data: dict): PacienteGeneral`

## Relaciones principales
El diagrama evidencia que:

- `PacienteGeneral` hereda de `Paciente`;
- `PacienteGeneralFactory` hereda de `PacienteFactory`;
- `PacienteGeneralFactory` crea instancias de `PacienteGeneral`.

## Beneficios en el proyecto
- desacopla al cliente de la clase concreta que se instancia;
- centraliza la lógica de creación de pacientes;
- facilita agregar nuevos tipos de pacientes en el futuro;
- mejora la organización y mantenibilidad del sistema;
- favorece el cumplimiento del principio de abierto/cerrado.

## Conclusión
El patrón Factory Method resulta adecuado para este módulo porque permite estructurar la creación de pacientes de forma clara, desacoplada y extensible, dejando preparada la solución para soportar nuevas variantes de paciente sin modificar el cliente.
