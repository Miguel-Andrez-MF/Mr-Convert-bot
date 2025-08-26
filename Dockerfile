FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .

# Instalar dependencias Python con optimizaciones
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Configurar variables de entorno para optimizar memoria
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV MALLOC_MMAP_THRESHOLD_=100000

RUN mkdir -p /app/temp


CMD ["python", "main.py"]