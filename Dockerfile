FROM python:3.11-slim
WORKDIR /app
# Copia e instala dependencias primero (mejor caché)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copia todo el proyecto
COPY . .
# Puerto de FastAPI
EXPOSE 8000
# Arranca uvicorn apuntando a backend/main.py
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
