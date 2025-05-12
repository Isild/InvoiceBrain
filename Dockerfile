# Bazowy obraz z Pythona
FROM python:3.11-slim

# Zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PGSERVICEFILE=/app/InvoiceBrain/.pg_service.conf
ENV PGPASSFILE=/app/InvoiceBrain/.pgpass


# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y netcat-openbsd gcc postgresql-client && apt-get clean

# Katalog roboczy
WORKDIR /app

# Kopiowanie plików projektu
COPY . /app/

CMD ["chmod", "0600", "InvoiceBrain/.pg_service.conf"]
CMD ["chmod", "0600", "InvoiceBrain/.pgpass"]

# Instalacja zależności z pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# TODO: add auto migrate and create elasticsearch 
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "search_index", "--rebuild"]

# Komenda domyślna
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
