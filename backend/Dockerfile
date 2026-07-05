FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema necesarias para algunos paquetes (mysqlclient, cryptography, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# El comando real lo define docker-compose (uvicorn ... --reload).
# Este CMD es el fallback si se ejecuta la imagen sola.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
