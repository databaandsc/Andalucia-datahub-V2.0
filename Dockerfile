# 1. IMAGEN BASE
FROM python:3.12-slim

# 2. DIRECTORIO DE TRABAJO
WORKDIR /app

# 3. VARIABLES DE ENTORNO
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. PREPARACIÓN DE POETRY
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# 5. CACHÉ DE DEPENDENCIAS
COPY pyproject.toml poetry.lock* ./

# 6. INSTALACIÓN: Instalamos las librerías de producción (FastAPI, SQLAlchemy, etc.)
RUN poetry install --only main --no-root --no-interaction

# 7. CÓDIGO FUENTE: Coipiamos el código fuente de la API al contenedor
COPY api/ ./api/

# 8. PUERTO
EXPOSE 8000

# 9. COMANDO FINAL
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]