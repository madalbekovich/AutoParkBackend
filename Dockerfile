# Auto Park backend — образ для gunicorn (API) и daphne (WebSocket).
FROM python:3.13-slim

# Не пишем .pyc, вывод сразу в лог (без буфера).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости (psycopg, pillow).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Сначала зависимости — кэшируется, пока requirements не меняется.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения.
COPY . .

# entrypoint должен быть исполняемым.
RUN chmod +x entrypoint.sh

EXPOSE 8000
