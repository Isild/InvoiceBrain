# Bazowy obraz z Pythona
FROM python:3.11-slim

# Zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PGSERVICEFILE=/app/InvoiceBrain/.pg_service.conf
ENV PGPASSFILE=/app/InvoiceBrain/.pgpass


# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y netcat-openbsd gcc postgresql-client && apt-get clean
RUN apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Katalog roboczy
WORKDIR /app

# Kopiowanie plików projektu
COPY . /app/

# Instalacja zależności z pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Komenda domyślna
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
