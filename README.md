# InvoiceBrain

- [General info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)
- [Documentation](#documentation)
- [Celery](#celery)
- [Elasticsearch](#elasticsearch)

## General info

This application is a sampler of my coding skills.
The project focus on API site without(for now) frontend.

## Technologies

[x] Python

[x] Django

[x] Celery

[x] Redis

[x] Elasticsearch

[x] Docker

[] Pandas

[] NumPy

[] RabbitMQ

[] OpenAI API invoices tags

[] Upload files to S3

[] JWT Auth

[] Elasticsearch work on entities in relationship + filtering + summary view

[] PySpark

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
`python manage.py createsuperuser`

If you want to see sended mail you can go to `http://localhost:8025`

! Fields with numbers are stored in int because later will be helper which convert number to float without losing precision.

Services like elastic and kibana can use a lot of memory. To handle it you can change RAM memory usage limit in docker-compose file: `mem_limit: 0.5g`

If entrypoint can't run application due to long time of setting up elastic instance then increase `max RetryTimes`.

Run all services may take a while.

## Documentation

At endpoints below you have docoumentation. You can choose which one you prefer:

- `/api/schema/swagger-ui/`
- `api/schema/redoc/`

# Celery

Used to sending notifications about:

- new invoice
- invoice was paid
- invoice payment date overdue

# Elasticsearch

App have searchs on invoice resource.

You can search at:

- invoice number at endpoint `/invoices/search-by-number`
- invoice companies name at endpoint `/invoices/search-by-companies`
- invoice dates at endpoint `/invoices/search-by-dates`
- invoice description and products list at endpoint `/invoices/search-by-descriptions-products`

Documentation for each endpoint can be found in [Documentation](#documentation) section

Here are specific implementation of elasticsearch to speed up searching. More functions with sophisticated filters will be implemented soon.
