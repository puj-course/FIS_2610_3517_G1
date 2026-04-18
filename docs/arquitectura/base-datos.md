#  Diagrama de Base de Datos – MedTrack

## Vista del Diagrama

![Diagrama de Base de Datos](https://github.com/user-attachments/assets/7d73735f-078e-43f8-b420-28022957e0d8)

---

## Descripción General

Este diagrama representa la estructura de datos del sistema **MedTrack**, el cual permite gestionar pacientes, medicamentos y el seguimiento de sus tratamientos.

El modelo está compuesto por las siguientes entidades principales:

- Pacientes  
- Medicamentos  
- Recordatorios  
- Tomas de medicamento  
- Alertas  

Estas entidades se relacionan para permitir el registro, control y monitoreo del tratamiento médico de cada paciente.

---

##  Entidades del Sistema

###  Pacientes
Almacena la información personal y médica del paciente.

**Campos principales:**
- `id` (PK)
- `nombres`
- `apellidos`
- `fecha_nacimiento`
- `género`
- `numero_documento`
- `diagnostico_principal`
- `alergias_conocidas`

---

###  Medicamentos
Contiene la información de los medicamentos asociados a cada paciente.

**Relación:**
- Un paciente puede tener múltiples medicamentos (1:N)

**Campos principales:**
- `id` (PK)
- `nombre`
- `concentracion`
- `dosis`
- `frecuencia`
- `horario`
- `paciente_id` (FK)

---

### Recordatorios
Define la programación de recordatorios para cada medicamento.

**Relación:**
- Un medicamento puede tener múltiples recordatorios (1:N)

**Campos principales:**
- `id` (PK)
- `medicamento_id` (FK)
- `hora_recordatorio`
- `fecha_inicio`
- `activo`

---

### Tomas de Medicamento
Registra cada toma programada o realizada por el paciente.

**Relaciones:**
- Paciente
- Medicamento
- Recordatorio

**Campos principales:**
- `id` (PK)
- `paciente_id` (FK)
- `medicamento_id` (FK)
- `recordatorio_id` (FK)
- `fecha_programada`
- `fecha_hora_toma`
- `estado`

---

###  Alertas
Gestiona notificaciones relacionadas con eventos importantes del tratamiento.

**Relaciones:**
- Paciente
- Medicamento
- Recordatorio

**Campos principales:**
- `id` (PK)
- `tipo`
- `mensaje`
- `severidad`
- `paciente_id` (FK)
- `medicamento_id` (FK)
- `recordatorio_id` (FK)
- `atendida`

---

## Relaciones del Modelo

- Un **paciente** tiene muchos **medicamentos**
- Un **medicamento** tiene muchos **recordatorios**
- Un **recordatorio** genera múltiples **tomas de medicamento**
- Las **alertas** pueden estar asociadas a pacientes, medicamentos o recordatorios

---

## Justificación del Diseño

El modelo es coherente con la lógica del negocio porque:

- Permite separar claramente las responsabilidades de cada entidad
- Facilita el seguimiento del tratamiento médico
- Permite registrar tanto la planificación como la ejecución de las tomas
- Soporta la generación de alertas ante eventos importantes
- Garantiza integridad de datos mediante el uso de claves foráneas

Además, el diseño es escalable y permite agregar nuevas funcionalidades sin afectar la estructura principal.

---

## Coherencia con el Código

Este diseño se refleja directamente en la implementación del sistema:

- Cada entidad corresponde a una tabla en la base de datos
- Las relaciones están implementadas mediante llaves foráneas
- Las funcionalidades del sistema (registro, seguimiento, alertas) se basan en este modelo

---

## Conclusión

El diagrama de base de datos proporciona una base sólida para el sistema, asegurando organización, consistencia y facilidad de mantenimiento, alineándose correctamente con los requerimientos del proyecto.
