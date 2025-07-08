# =========================================================================
# ETAPA 1: BUILDER - Prepara el entorno y las dependencias
# =========================================================================
FROM python:3.10-slim-bookworm AS builder

# Establecemos variables de entorno para buenas prácticas con Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos y establecemos el directorio de trabajo
WORKDIR /app

# Actualizamos los paquetes del sistema operativo
RUN apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Creamos un entorno virtual aislado
RUN python -m venv /opt/venv

# Activamos el entorno virtual para los siguientes comandos RUN
ENV PATH="/opt/venv/bin:$PATH"

# Copiamos el archivo de dependencias
COPY requirements.txt .

# ===================================================================
# PASO DE CORRECCIÓN: Actualizamos las herramientas base de Python
# ANTES de instalar las dependencias de la aplicación.
# Esto soluciona las vulnerabilidades encontradas por Trivy.
# ===================================================================
RUN pip install --upgrade pip setuptools wheel

# Instalamos las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt


# =========================================================================
# ETAPA 2: FINAL - Construye la imagen de producción final
# =========================================================================
FROM python:3.10-slim-bookworm

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos ÚNICAMENTE el entorno virtual con las dependencias ya instaladas
COPY --from=builder /opt/venv /opt/venv

# Copiamos el código fuente de nuestra aplicación
COPY ./core ./core
COPY ./db ./db
COPY ./services ./services
COPY ./api ./api
COPY main.py .

# Activamos el entorno virtual para el comando de ejecución final
ENV PATH="/opt/venv/bin:$PATH"

# Exponemos el puerto en el que correrá nuestra aplicación FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación en modo producción usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]