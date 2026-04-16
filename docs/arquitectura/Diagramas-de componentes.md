# Escenario — Recordatorios

## Descripción general
Este escenario reúne los diagramas de componentes asociados a la funcionalidad de recordatorios. En conjunto, muestran cómo se organiza el sistema para crear, editar, activar o desactivar recordatorios, integrando la interfaz del usuario, la lógica del sistema, las validaciones, la API REST y la persistencia.

---

## Diagrama de componentes 1
![Componentes Recordatorios 1](./imagenes/componentes-recordatorios-1.png)

### Explicación
Este diagrama presenta una vista general del **Sistema de recordatorio** como componente central, conectado con los módulos principales del sistema:

- **Gestión Recordatorios**, donde se agrupan:
  - `EditarRecordatorio`
  - `ActivarDesactivar`
  - `CrearRecordatorio`
- **Medicamentos**, con:
  - `ModeloMedicamento`
  - `RelacionFK`
- **Persistencia**, compuesta por:
  - `TablaRecordatorios`
  - `TablaMedicamentos`
- **Cliente**, con:
  - `InterfazUsuario`
  - `FormularioRecordatorio`
- **API REST**, que incluye:
  - `ValidacionDatos`
  - `EndpointsRecordatorios`

### Justificación
Este diagrama muestra cómo la funcionalidad de recordatorios depende de varios módulos del sistema y cómo todos se articulan alrededor del componente central. Esto permite entender la relación entre cliente, lógica de negocio, persistencia y API.

---

## Diagrama de componentes 2
![Componentes Recordatorios 2](./imagenes/componentes-recordatorios-2.png)

### Explicación
Este segundo diagrama profundiza en el flujo de creación de recordatorios. Se observa cómo el **Formulario Recordatorio** se compone de:

- `SelectorDias`
- `SelectorHora`
- `InputMedicamento`
- `InputDosis`
- `InputObservaciones`

Además, se conectan los componentes de:

- **Validaciones**
  - `CamposObligatorios`
  - `ValidacionFormatoHora`
- **Gestión Recordatorios**
  - `CrearRecordatorio`
- **Persistencia**
  - `TablaRecordatorios`
- **API REST**
  - `RecepcionDatos`
  - `EndpointsRecordatorios`
- **Cliente**
  - `InterfazUsuario`
  - `FormularioRecordatorio`

### Justificación
Este diagrama permite ver con mayor detalle la interacción interna de la funcionalidad, especialmente el rol del formulario, las validaciones y la comunicación con la API y la base de datos.

## Conclusión
Los dos diagramas se complementan entre sí: el primero presenta la arquitectura general del sistema de recordatorios y el segundo muestra con mayor detalle el flujo específico de creación y validación.


# Escenario — Registro de medicamentos

## Descripción general
Este escenario reúne los diagramas de componentes relacionados con la funcionalidad de registro de medicamentos. En conjunto, muestran cómo el sistema organiza la captura de datos, la validación, la lógica de negocio, la persistencia y la retroalimentación al usuario.

---

## Diagrama de componentes 1
![Componentes Registro Medicamentos 1](./imagenes/componentes-registro-medicamentos-1.png)

### Explicación
Este diagrama muestra la interacción entre los componentes que participan en el registro de medicamentos:

- **Cliente**
  - `InterfazUsuario`
  - `FormularioRecordatorio`
- **Formulario Recordatorio**
  - `SelectorDias`
  - `SelectorHora`
  - `InputMedicamento`
  - `InputDosis`
  - `InputObservaciones`
- **Validaciones**
  - `CamposObligatorios`
  - `ValidacionFormatoHora`
  - `ControlErrores`
- **API REST**
  - `RecepcionDatos`
  - `EndpointsRecordatorios`
- **Gestión medicamentos**
  - `RegistrarMedicamento`
- **Persistencia**
  - `TablaMedicamentos`
- **Mensaje**
  - `Mensajeerror`
  - `MensajeExito`

### Justificación
Este diagrama evidencia cómo el registro de medicamentos se apoya en distintos módulos especializados, permitiendo separar la captura de datos, la validación, el almacenamiento y la notificación al usuario.

---

## Diagrama de componentes 2
![Componentes Registro Medicamentos 2](./imagenes/componentes-registro-medicamentos-2.png)

### Explicación
Este segundo diagrama muestra una vista más enfocada en la relación entre:

- **API REST**
  - `RecepcionDatos`
  - `EndpointsRecordatorios`
- **Gestión medicamentos**
  - `RegistrarMedicamento`
- **Persistencia**
  - `TablaMedicamentos`
- **Cliente**
  - `InterfazUsuario`
  - `FormularioRecordatorio`
- **Formulario Recordatorio**
  - `SelectorDias`
  - `SelectorHora`
  - `InputMedicamento`
  - `InputDosis`
  - `InputObservaciones`
- **Validaciones**
  - `CamposObligatorios`
  - `ValidacionFormatoHora`
- **Mensaje**
  - `Mensajeerror`
  - `MensajeExito`

### Justificación
Este diagrama permite complementar la visión del primero, resaltando cómo el flujo de datos del formulario llega hasta la capa de persistencia y cómo el sistema devuelve retroalimentación al usuario después del proceso.

## Conclusión
Los dos diagramas ofrecen una visión complementaria del registro de medicamentos, mostrando tanto la estructura general de componentes como el detalle del flujo entre formulario, validaciones, API, persistencia y mensajes.


# Escenario — Registro de pacientes

## Descripción general
Este escenario reúne los diagramas asociados a la funcionalidad de registro de pacientes. En conjunto, permiten comprender la relación entre la interfaz, las validaciones, la lógica de negocio y la persistencia.

---

## Diagrama 1
![Diagrama 1](./imagenes/registro-pacientes-1.png)

### Explicación
Aquí describes el primer diagrama.

### Justificación
Aquí explicas por qué ese diagrama representa bien la funcionalidad.

---

## Diagrama 2
![Diagrama 2](./imagenes/registro-pacientes-2.png)

### Explicación
Aquí describes el segundo diagrama.

### Justificación
Aquí explicas por qué complementa al primero.

## Conclusión
Ambos diagramas permiten entender de forma más completa la funcionalidad de registro de pacientes.
