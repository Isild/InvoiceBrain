#!/bin/sh

it=0
maxRetryTimes=30

set -e

chmod 600 InvoiceBrain/.pgpass
chmod 600 InvoiceBrain/.pg_service.conf
echo "Configured pgpass file\n"

echo "Starting migrations DB\n"
python manage.py migrate
echo "DB migrations successfully executed"

echo "Waiting for Elasticsearch...\n"

while ! curl -s http://elastic:9200 >/dev/null;
do 
    echo "Elasticsearch is not connected"
    sleep 2
    it=$((it+1))

    if [ "$it" -eq "$maxRetryTimes" ]; then
        break
    fi
done



if [ "$it" -lt "$maxRetryTimes" ]; then
    echo "Starting setup elasticsearch data\n"
    echo "Are you sure you want to delete the 'invoices' indices? [y/N]: y" | python manage.py search_index --rebuild -f
    echo "Setup elasticsearch data successfully compleated"
fi

echo "Starting create periodic tasks"
python manage.py create_periodic_tasks
echo "Creating periodic tasks successfully compleated"

echo "Now running the Django application"
python manage.py runserver 0.0.0.0:8000
