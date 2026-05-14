## 🩺 MedTrack
## 📌 Descripción

MedTrack es una solución de software orientada al seguimiento y control de la administración de medicamentos, diseñada especialmente para cuidadores novatos, es decir, personas que asumen el cuidado de pacientes sin formación médica previa.

En muchos contextos de cuidado informal, el control de medicamentos se realiza mediante notas manuales, alarmas genéricas o la memoria del cuidador, aumentando el riesgo de olvidos, errores de dosificación y falta de trazabilidad del tratamiento.

MedTrack busca centralizar y organizar toda la información relacionada con pacientes, medicamentos, recordatorios e historial de tomas en una sola plataforma, permitiendo reducir la carga cognitiva del cuidador y mejorar el seguimiento del tratamiento de forma segura y estructurada.

Este proyecto fue desarrollado como iniciativa académica dentro de la asignatura Fundamentos de Ingeniería de Software de la Pontificia Universidad Javeriana.

## 💭 Idea del proyecto

La administración de medicamentos es una tarea crítica dentro del cuidado de pacientes, especialmente en tratamientos prolongados o complejos. Cuando esta responsabilidad recae sobre personas sin experiencia médica, la probabilidad de errores aumenta significativamente.

MedTrack surge como una propuesta para acompañar al cuidador mediante una herramienta clara, intuitiva y adaptable, permitiendo:

Llevar un registro estructurado de tratamientos.
Controlar horarios y dosis.
Evitar duplicación de medicamentos.
Generar recordatorios automáticos.
Registrar historial de tomas.
Obtener métricas de adherencia al tratamiento.
## ❓ Problemática identificada

MedTrack busca resolver:

Falta de seguimiento estructurado en tratamientos médicos.
Olvidos en horarios de administración.
Confusión entre medicamentos y dosis.
Ausencia de historial de tomas.
Dificultad para validar cumplimiento del tratamiento.
Riesgo de errores por parte de cuidadores sin experiencia médica.
## 👥 Público objetivo

La solución está orientada principalmente a:

Cuidadores sin formación médica.
Familias encargadas del cuidado de pacientes.
Personas con múltiples pacientes bajo supervisión.
Pacientes con tratamientos prolongados.
## 🎯 Propuesta de valor

MedTrack se diferencia de aplicaciones genéricas de recordatorios al enfocarse específicamente en el contexto real del cuidador novato.

La plataforma prioriza:

Claridad y simplicidad visual.
Prevención de errores comunes.
Historial trazable de administración.
Seguimiento estructurado del tratamiento.
Alertas inteligentes y automatizadas.
Organización centralizada de la información médica.
## 🧩 Características principales
# 👤 Gestión de pacientes
Registro y administración de pacientes.
Información médica y observaciones relevantes.
Historial individual por paciente.
# 💊 Gestión de medicamentos
Registro de medicamentos y dosis.
Configuración de horarios y frecuencias.
Validación de duplicados y conflictos.
# ⏰ Recordatorios automáticos
Programación de recordatorios.
Seguimiento de tomas pendientes.
Notificaciones automáticas mediante Telegram.
# 📋 Historial de tomas
Registro de adherencia al tratamiento.
Clasificación de tomas:
A tiempo
Tarde
Pendiente
Omitida
# 📊 Resumen y métricas
Porcentaje de cumplimiento.
Historial consolidado.
Alertas relevantes del tratamiento.
# 🔐 Seguridad
Autenticación JWT.
Middleware de protección de rutas.
Roles de usuario.
# 🛠️ Tecnologías utilizadas
*Frontend
React
JavaScript
CSS
*Backend
FastAPI
Python 3.11
PyJWT
Pydantic
*Base de datos
MongoDB Atlas
*Testing y Calidad
Pytest
GitHub Actions
SonarQube Cloud
*DevOps
Docker
Docker Compose
*CI/CD automatizado
Integraciones
Telegram Bot API
## 🏗️ Arquitectura del sistema

La arquitectura de MedTrack está basada en una separación cliente-servidor:

Frontend React/Vite
        ↓
Backend FastAPI
        ↓
MongoDB Atlas

El sistema utiliza autenticación JWT para proteger endpoints y GitHub Actions para automatizar pruebas y procesos de integración continua.

## 📁 Estructura del proyecto
MedTrack/
│
├── .github/
│   └── workflows/
│
├── backend/
│   ├── alertas/
│   ├── commands/
│   ├── decorators/
│   ├── factories/
│   ├── middleware/
│   ├── routes/
│   ├── services/
│   ├── states/
│   ├── auth.py
│   ├── database.py
│   ├── historial_toma.py
│   ├── main.py
│   ├── models.py
│   ├── scheduler.py
│   ├── toma_repository.py
│   ├── validaciones.py
│   └── requirements.txt
│
├── medtrack-app/
│   ├── public/
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│
├── docs/
│
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt

## 📋 Requisitos
Python 3.11+
Node.js 18+
MongoDB Atlas
Docker (opcional)

## 🧪 Ejecución de pruebas
Ejecutar todos los tests
python -m pytest -v tests/
Generar reportes HTML/XML
pytest tests/ --junitxml=report.xml --html=report.html --self-contained-html
## 🔄 CI/CD

El proyecto implementa pipelines automáticos mediante GitHub Actions para:

Ejecución automática de pruebas.
Validación de dependencias.
Reportes HTML/XML.
Integración continua.
Análisis de calidad.
Notificaciones automáticas mediante Telegram.
## 📊 Calidad del software

El proyecto utiliza:

SonarQube Cloud
Métricas de mantenibilidad
Pruebas automatizadas
Validaciones backend
Cobertura funcional

## 🤝 Equipo del proyecto
## Equipo del Proyecto

| Nombre completo        | Rol en el proyecto                              | GitHub / Perfil |
|------------------------|-------------------------------------------------|-----------------------------------------|
| Natalia Quiñonez       | Scrum Master                                    | https://github.com/Naqz05               |
| Sofía Sierra           | Propietario del producto                        | https://github.com/sofia-sierra2        |
| Valentina Cano         | Planificador de sprints                         | https://github.com/Valentina866         |
| Vanesa Ramos           | Administrador de configuración                  | https://github.com/vanexalram           |
| Andrés Felipe Díaz     | Responsable de control de calidad (QA Lead)     | https://github.com/rodríguezdiazandres8 |
| Karol Torres           | Ingeniero de DevOps                             | https://github.com/TorresVides          |




### Roles y responsabilidades

- **Scrum Master**: Organiza el trabajo por sprints, facilita ceremonias Scrum, da seguimiento al avance del proyecto y gestiona impedimentos.
- **Product Owner**: Lidera la recolección de requerimientos, define y prioriza el Product Backlog, valida entregables y cierra issues.
- **Sprint Planner**: Descompone historias de usuario en tareas, organiza el backlog del sprint y asegura coherencia entre sprints, issues y backlog.
- **Configuration Manager**: Administra el repositorio, controla el Gitflow, revisa y aprueba pull requests y supervisa versiones.
- **Quality Assurance Lead (QA Lead)**: Verifica el cumplimiento de criterios de evaluación, revisa calidad funcional, técnica y documental, y reporta defectos.
- **DevOps Engineer**: Diseña y mantiene pipelines CI/CD, automatiza pruebas, gestiona despliegues con Docker y configura entornos.

```

## 📌 Contexto académico

Asignatura: Fundamentos de Ingeniería de Software

Docente: Luis Gabriel Moreno Sandoval, PhD

Institución: Pontificia Universidad Javeriana

## Contacto del equipo
1. Natalia Quiñonez Zaia
  Estudiante Ing. sistemas
  nataliaa-quinonez@javeriana.edu.co
3. Sofia Sierra
   Estudiante Ing. sistemas
   sofia-sierra@javeriana.edu.co
5. Valentina Cano
   Estudiante Ing. sistemas
   dvalentina-cano@javeriana.edu.co
7. Vanesa Ramos
   Estudiante Ing. sistemas
   vanesaa_ramos@javeriana.edu.co
9. Andrés Felipe Díaz
   Estudiante Ing. sistemas
   Diaz.afelipe@javeriana.edu.co
11. Karol Torres
    Estudiante Ing. sistemas
    torres_kdayan@javeriana.edu.co
    
📄 Licencia
Proyecto desarrollado con fines académicos.
