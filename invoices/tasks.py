from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Invoice
from utils.redis_client import redis_client
from redis.exceptions import WatchError

@shared_task
def check_overdue_invoices():

    now_date = timezone.now()
    overdue_invoices = Invoice.objects.filter(payment_date__isnull=True, payment_due_date__lt=now_date)

    for invoice in overdue_invoices:
        redis_key = f'invoice:{invoice.id}:to-notifie'

        if not redis_client.get(redis_key) and invoice.outstanding_unpaid(now_date) and not invoice.sended_overdude_notification_at:
            redis_client.set(redis_key, '1', ex=86400*2)


@shared_task
def send_overdude_invoide_notification():
    subject = "Overdue"
    email = "test@test.pl"
    redis_key_pattern = "invoice:*:to-notifie"

    for key in redis_client.scan_iter(match=redis_key_pattern):
        invoice_id = key.split(':')[1]

        with redis_client.pipeline() as pipe:
            try:
                pipe.watch(key)

                if pipe.get(key) == '1':
                    message = f"Invoice is overdue, ID: {invoice_id}"

                    send_mail(subject, message, 'no-reply@invoicebrain.com', [email])

                    updated = Invoice.objects.filter(id=invoice_id, sended_overdude_notification_at=None).update(sended_overdude_notification_at=timezone.now())

                    if updated:
                        pipe.delete(f'invoice:{invoice_id}:to-notifie')
                    # TODO: add else throwing error with that notification

                    pipe.execute()

            except WatchError:
                continue
            # TODO: add send mail errors handling
            finally:
                redis_client.unwatch()
