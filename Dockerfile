# --- Fase 1: Constructor (Builder) ---
FROM python:3.12-slim AS builder

# Evita que Python genere archivos .pyc y permite que los logs fluyan
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalo dependencias del sistema necesarias para compilar psycopg2 si fuera necesario
# (Aunque usamos binary, es buena práctica tener el entorno listo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Creo un entorno virtual para aislar las dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Fase 2: Ejecución (Final) ---
FROM python:3.12-slim

WORKDIR /app

# Copio solo el entorno virtual con las dependencias instaladas
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copio el código fuente
COPY src/ /app/src/

# Configuración de usuario no-root por seguridad
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Puerto por defecto para Cloud Run (Google Cloud asigna el puerto en la variable PORT)
ENV PORT=8000

# Comando para iniciar la aplicación usando uvicorn
# Usamos 0.0.0.0 para que sea accesible desde fuera del contenedor
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT
