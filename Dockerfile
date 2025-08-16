FROM python:3.11-slim

# Instalar dependencias del sistema (poppler para pdf2image)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar requirements primero (mejor cache)
COPY bot/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY bot/ .

# Comando para correr el bot
CMD ["python", "main.py"]