<<<<<<< HEAD
# fis_boilerplate
## Descripción de cada directorio y archivos
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
├── Dockerfile
├── docker-compose.yml
└── Makefile
```


### .github/
Contiene configuraciones específicas para GitHub, como plantillas para problemas (issues) y solicitudes de extracción (pull requests), y flujos de trabajo de GitHub Actions para integración continua (CI) y despliegue continuo (CD).

- `ISSUE_TEMPLATE/`: Plantillas para reportar bugs y solicitar nuevas características.
- `workflows/`: Archivos YAML para definir los flujos de trabajo de CI/CD.

### docs/
Documentación del proyecto.

- `api/`: Documentación de la API.
- `architecture/`: Diagramas y documentación de la arquitectura.
- `user_guide/`: Guías para usuarios.

### src/
Código fuente del proyecto.

- `main/`: Código fuente principal.
  - `java/` (o `python/`, etc.): Código fuente del proyecto según el lenguaje utilizado.
  - `resources/`: Archivos de recursos como configuraciones y otros archivos necesarios.
- `test/`: Código de pruebas.
  - `java/` (o `python/`, etc.): Código de pruebas unitarias y de integración.
  - `resources/`: Archivos de recursos para las pruebas.

### scripts/
Scripts útiles para tareas comunes como configuración, despliegue y pruebas.

- `setup.sh`: Script para configurar el entorno de desarrollo.
- `deploy.sh`: Script para despliegue.
- `test.sh`: Script para ejecutar pruebas.

### conf/
Carpeta para archivos de configuración.

- `config.yaml`: Archivo de configuración en formato YAML.
- `settings.json`: Archivo de configuración en formato JSON.

### jupyter/
Carpeta para los notebooks de Jupyter y datasets utilizados.

- `notebooks/`: Carpeta para los notebooks de Jupyter.
  - `exploration.ipynb`: Notebook para la exploración de datos.
  - `analysis.ipynb`: Notebook para el análisis de datos.
- `datasets/`: Carpeta para los datasets utilizados en los notebooks.
  - `data1.csv`: Ejemplo de dataset en formato CSV.
  - `data2.csv`: Otro ejemplo de dataset en formato CSV.

### temp/
Carpeta para archivos temporales.

- `temp_file.txt`: Archivo temporal de ejemplo.
- `temp_data/`: Subcarpeta para datos temporales.
  - `temp1.tmp`: Archivo temporal de ejemplo.
  - `temp2.tmp`: Otro archivo temporal de ejemplo.

### Archivos en la raíz del proyecto

- `.gitignore`: Archivo para especificar qué archivos y directorios deben ser ignorados por Git.
- `README.md`: Descripción general del proyecto, instrucciones de instalación, uso, contribución, etc.
- `LICENSE`: Información sobre la licencia del proyecto.
- `CHANGELOG.md`: Registro de cambios en el proyecto.
- `CONTRIBUTING.md`: Guía para contribuir al proyecto.
- `Dockerfile`: Archivo para construir la imagen Docker del proyecto.
- `docker-compose.yml`: Archivo de configuración para Docker Compose.
- `Makefile`: Archivo para automatizar tareas mediante comandos `make`.

=======
# fis_boilerplate
## Descripción de cada directorio y archivos
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
│   │   ├── backend/          //BACKEND
│   │   │   ├── models.py
│   │   │   ├── auth.py
│   │   │   ├── app.py
│   │   │   └── seed.py
│   │   └── frontend/       //FRONTEND
│   │       ├── login.html
│   │       └── dashboard.html
│   └── tests/
│       └── test/          //PRUEBAS
│           └── test_auth.py
│   ├── temp_file.txt
│   └── temp_data/
│       ├── temp1.tmp
│       └── temp2.tmp
├── .gitignore
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── docker-compose.yml
└── Makefile
```


### .github/
Contiene configuraciones específicas para GitHub, como plantillas para problemas (issues) y solicitudes de extracción (pull requests), y flujos de trabajo de GitHub Actions para integración continua (CI) y despliegue continuo (CD).

- `ISSUE_TEMPLATE/`: Plantillas para reportar bugs y solicitar nuevas características.
- `workflows/`: Archivos YAML para definir los flujos de trabajo de CI/CD.

### docs/
Documentación del proyecto.

- `api/`: Documentación de la API.
- `architecture/`: Diagramas y documentación de la arquitectura.
- `user_guide/`: Guías para usuarios.

### src/
Código fuente del proyecto.

- `main/`: Código fuente principal.
  - `java/` (o `python/`, etc.): Código fuente del proyecto según el lenguaje utilizado.
  - `resources/`: Archivos de recursos como configuraciones y otros archivos necesarios.
- `test/`: Código de pruebas.
  - `java/` (o `python/`, etc.): Código de pruebas unitarias y de integración.
  - `resources/`: Archivos de recursos para las pruebas.

### scripts/
Scripts útiles para tareas comunes como configuración, despliegue y pruebas.

- `setup.sh`: Script para configurar el entorno de desarrollo.
- `deploy.sh`: Script para despliegue.
- `test.sh`: Script para ejecutar pruebas.

### conf/
Carpeta para archivos de configuración.

- `config.yaml`: Archivo de configuración en formato YAML.
- `settings.json`: Archivo de configuración en formato JSON.

### jupyter/
Carpeta para los notebooks de Jupyter y datasets utilizados.

- `notebooks/`: Carpeta para los notebooks de Jupyter.
  - `exploration.ipynb`: Notebook para la exploración de datos.
  - `analysis.ipynb`: Notebook para el análisis de datos.
- `datasets/`: Carpeta para los datasets utilizados en los notebooks.
  - `data1.csv`: Ejemplo de dataset en formato CSV.
  - `data2.csv`: Otro ejemplo de dataset en formato CSV.

### temp/
Carpeta para archivos temporales.

- `temp_file.txt`: Archivo temporal de ejemplo.
- `temp_data/`: Subcarpeta para datos temporales.
  - `temp1.tmp`: Archivo temporal de ejemplo.
  - `temp2.tmp`: Otro archivo temporal de ejemplo.

### Archivos en la raíz del proyecto

- `.gitignore`: Archivo para especificar qué archivos y directorios deben ser ignorados por Git.
- `README.md`: Descripción general del proyecto, instrucciones de instalación, uso, contribución, etc.
- `LICENSE`: Información sobre la licencia del proyecto.
- `CHANGELOG.md`: Registro de cambios en el proyecto.
- `CONTRIBUTING.md`: Guía para contribuir al proyecto.
- `Dockerfile`: Archivo para construir la imagen Docker del proyecto.
- `docker-compose.yml`: Archivo de configuración para Docker Compose.
- `Makefile`: Archivo para automatizar tareas mediante comandos `make`.

>>>>>>> develop
