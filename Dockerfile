# =========================================================================
# ETAPA 1: BUILDER - Prepara el entorno y las dependencias
# =========================================================================
# Usamos un alias "builder" para esta etapa para poder referenciarla después.
FROM python:3.10-slim-bookworm AS builder

# Establecemos variables de entorno para buenas prácticas con Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Creamos y establecemos el directorio de trabajo
WORKDIR /app

# Creamos un entorno virtual aislado dentro de nuestro contenedor.
# Esto es una práctica robusta para evitar conflictos y mantener limpio el sistema base.
RUN apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

# Activamos el entorno virtual para los siguientes comandos RUN
ENV PATH="/opt/venv/bin:$PATH"

# Copiamos el archivo de dependencias
COPY requirements.txt .

# Instalamos TODAS las dependencias (incluyendo las de desarrollo) en el venv.
# Las librerías de prueba y calidad son necesarias en etapas posteriores del CI,
# pero no las incluiremos en la imagen final.
RUN pip install --no-cache-dir -r requirements.txt


# =========================================================================
# ETAPA 2: FINAL - Construye la imagen de producción final
# =========================================================================
# Empezamos de nuevo desde la misma imagen base limpia.
FROM python:3.10-slim-bookworm

# Establecemos el directorio de trabajo
WORKDIR /app

# --- La Magia del Multi-etapa ---
# Copiamos ÚNICAMENTE el entorno virtual con las dependencias ya instaladas
# desde la etapa 'builder'. No traemos nada más de esa etapa.
COPY --from=builder /opt/venv /opt/venv

# Copiamos el código fuente de nuestra aplicación.
# Al separar por carpetas, aprovechamos mejor el caché de Docker.
COPY ./core ./core
COPY ./db ./db
COPY ./services ./services
COPY ./api ./api
COPY main.py .

# Activamos el entorno virtual para el comando de ejecución final.
ENV PATH="/opt/venv/bin:$PATH"

# Exponemos el puerto en el que correrá nuestra aplicación FastAPI.
EXPOSE 8000

# Comando para ejecutar la aplicación en modo producción usando Uvicorn.
# Escucha en todas las interfaces de red (0.0.0.0) en el puerto 8000.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]