# InvoiceBrain

- [General info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)
- [More detailed information about modules](#more-detailed-information-about-modules)
- [Application view](#application-view)
- [Celery](#celery)

## General info

This application is a sampler of my coding skills.
The project focus on API site without(for now) frontend.

## Technologies

[x] Python

[x] Django

[] RabbitMQ

[x] Celery

[x] Redis

[x] Elasticsearch

[] Pandas

[] NumPy

[] OpenAI API

[x] Docker

[] JWT Auth

## Setup

First you must copy:
`./InvoiceBrain/.example.pg_service.conf` to `./InvoiceBrain/.pg_service.conf`
`./InvoiceBrain/.example.pgpass` to `./InvoiceBrain/.pgpass`
This filles will store credentials to connect to PostgreSQL.

Add `chmod +x entrypoint.sh`

To run application type command `docker-compose up`

When all containers are running get into `invoicebrain_web_1` container.
Then run db migrations `python manage.py migrate` and create Elasticsearch datas `python manage.py search_index --rebuild`.
Run `python manage.py migrate django_celery_beat` to create cron table. // zobaczyć czy się czasami nie uruchamia

You can also create superuser to see data in django admin page.

If you want to see sended mail you can go to `http://localhost:8025`

# Celery

Used to sending notifications about:

- new invoice
- invoice was paid
- invoice payment date overdue
