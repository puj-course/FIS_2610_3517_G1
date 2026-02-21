# 🩺 MedTrack
## Descripción

MedTrack es un proyecto de software orientado a apoyar el seguimiento y control de la administración de medicamentos, con un enfoque especial en cuidadores novatos, es decir, personas que asumen el cuidado de un paciente sin formación médica previa.

En muchos contextos, el control de medicamentos se realiza de forma manual mediante notas, alarmas genéricas o la memoria del cuidador, lo que puede provocar olvidos, confusión de horarios, duplicación de dosis o falta de información clara sobre si un medicamento ya fue administrado. Estas situaciones incrementan el riesgo de errores y afectan directamente la efectividad del tratamiento.

MedTrack busca centralizar y organizar la información del paciente y su medicación en un solo lugar, facilitando el seguimiento diario y reduciendo la carga cognitiva del cuidador, permitiéndole cumplir sus responsabilidades de forma más segura y confiable.

Este proyecto se desarrolla como una iniciativa académica y evolutiva dentro de la asignatura Fundamentos de Ingeniería de Software.

## 💭 Idea del proyecto

La administración de medicamentos es una tarea crítica dentro del cuidado de pacientes, especialmente en tratamientos prolongados. Cuando esta labor recae en cuidadores sin experiencia médica, el riesgo de errores aumenta significativamente.
MedTrack surge como una propuesta para acompañar al cuidador, ofreciendo una herramienta clara, intuitiva y adaptable que permita llevar un registro estructurado del tratamiento, facilitando el cumplimiento de horarios, dosis y observaciones relevantes. En especial, cuando el cuidador tiene más de un paciente bajo su cuidado.

## ❓ ¿Qué problema resuelve?

- Falta de seguimiento estructurado en la administración de medicamentos.

- Olvidos o confusión en horarios y dosis.

- Dificultad para saber si un medicamento ya fue administrado.

- Ausencia de un historial claro de tomas que permita identificar fallos en la adherencia al tratamiento.

- Riesgo de errores por parte de cuidadores sin formación médica.

## 👥 ¿A quién afecta?

Este problema impacta principalmente a:

- Personas cuidadoras sin experiencia médica.

- Familias a cargo del cuidado de pacientes.

- Pacientes con tratamientos prolongados o complejos.

## 🎯 Propuesta de valor

MedTrack ofrece valor al enfocarse en un problema específico que suele ser ignorado por muchas aplicaciones de seguimiento de medicamentos: la experiencia del cuidador novato en contextos reales de cuidado no clínico.

A diferencia de soluciones genéricas orientadas a pacientes autónomos o personal médico, MedTrack está diseñada para personas sin formación médica que asumen la responsabilidad del cuidado diario, muchas veces de manera repentina y sin acompañamiento técnico.

El proyecto prioriza:

- Claridad y simplicidad en la presentación de la información, reduciendo la carga cognitiva del cuidador.
- Prevención de errores comunes en contextos reales de uso (olvidos, duplicación de dosis, confusión entre medicamentos).
- Registro trazable del tratamiento, no solo como recordatorio, sino como evidencia del cumplimiento.
- Apoyo al proceso de toma de decisiones cotidianas en el cuidado, más allá de simples alertas.

MedTrack no busca reemplazar sistemas clínicos, sino cubrir el vacío existente entre el cuidado informal y las herramientas médicas especializadas.


## 🧩 ¿Qué lo hace diferente?

A diferencia de alarmas genéricas o aplicaciones ya existentes enfocadas en usuarios expertos, MedTrack se centra en el cuidador novato, priorizando la claridad, la simplicidad y la personalización de la información.

La aplicación no solo recuerda qué medicamento tomar, sino que construye un historial comprensible del tratamiento, permitiendo identificar patrones de cumplimiento y facilitando la comunicación futura con profesionales de la salud si es necesario.

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

## 🚀 Enfoque del proyecto

- Proyecto basado en un problema real del cuidado de pacientes.
- Coherencia entre el problema identificado, la solución propuesta y el valor ofrecido.
- Desarrollo guiado por metodologías ágiles (Scrum).
- Uso de GitHub para la gestión del proyecto, issues, sprints y seguimiento.
- Proyecto evolutivo, susceptible a ajustes durante el curso.


## Tecnologías Utilizadas
- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Python , Flask
- **Base de Datos:** SQLite
- **Control de versiones:** Git / GitHub
- **DevOps / CI:** GitHub Actions (si aplica)

---

## Estructura del Proyecto
```bash
MedTrack/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── conf/
│   ├── config.yaml
│   └── settings.json
├── docs/
│   ├── api/
│   ├── architecture/
│   └── user_guide/
├── jupyter/
│   ├── notebooks/
│   │   ├── exploration.ipynb
│   │   └── analysis.ipynb
│   └── datasets/
│       ├── data1.csv
│       └── data2.csv
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── test.sh
├── src/
│   ├── main/
│   │   ├── backend/   //BACKEND
│   │   │   ├── models.py
│   │   │   ├── auth.py
│   │   │   ├── database.db
│   │   │   ├── requirements.txt
│   │   │   ├── routes/
│   │   │   |   ├── auth_route.py
│   │   └── frontend/       //FRONTEND
│   │       ├── login.html
│   │       └── dashboard.html
│   └── test/
│       └── tests/          //PRUEBAS
│           └── test_auth.py
│   ├── temp_file.txt
│   └── temp_data/
│       ├── temp1.tmp
│       └── temp2.tmp
├── .gitignore
├── README.md
├── LICENSE
├── requirements.txt
├── CHANGELOG.md
├── CONTRIBUTING.md
└── Makefile
```

## Instalación y Ejecución
### Requisitos
- Git
- Python 3.10+

---

### Clonar el repositorio

```bash
git clone https://github.com/puj-course/FIS_2610_3517_G1.git
cd FIS_2610_3517_G1 
```

### Instalar dependencias

```bash
python -m pip install -r src/main/backend/requirements.txt
```

## Ejecución del proyecto


```bash
cd src/main/backend
pyton models.py
pyton app.py
```
## Ejecución de pruebas


```bash
cd src/test/tests
pytest test_auth.py
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

- Valentina Cano
- https://github.com/Valentina866
📄 Licencia

Proyecto desarrollado con fines académicos.
