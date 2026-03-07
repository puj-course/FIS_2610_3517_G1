plaintext
FIS_2610_3517_G1/
├── conf/
│   └── .gitkeep
├── backend/
│   ├── routes/
│   │   ├── auth_route.py           - Endpoints de autenticación (signin, signup)
│   │   └── patient_route.py        - Endpoints de registro y consulta de pacientes
│   ├── __init__.py                 - Inicialización del módulo backend
│   ├── auth.py                     - Lógica de encriptación de contraseñas y JWT
│   ├── main.py                     - Punto de entrada de la aplicación FastAPI
│   ├── models.py                   - Conexión a la base de datos e inicialización de tablas
│   ├── seed.py                     - Script para crear usuario de prueba inicial
│   ├── validaciones.py             - Validaciones y manejo de errores del registro de paciente
│   ├── database.db                 - Base de datos SQLite
│   └── requirements.txt            - Dependencias del backend
├── frontend/
│   ├── login.html                  - Interfaz de inicio de sesión
│   ├── dashboard.html              - Panel principal
│   ├── patients.html               - Listado de pacientes
│   └── RegistrarPaciente.html      - Formulario de registro de paciente
├── tests/
│   ├── test_auth.py                - Pruebas funcionales de autenticación
│   └── test_paciente.py            - Pruebas funcionales de registro de paciente
├── .gitignore
├── BOILERPLATE.md                  - Estructura del proyecto
├── LICENSE
├── README.md
└── requirements.txt                - Dependencias generales
 ⁠
