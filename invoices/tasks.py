from celery import shared_task
from django.utils import timezone
from redis.exceptions import WatchError

from invoices.services.invoice_notifications import InvoiceNotificationService
from utils.redis_client import redis_client

from .models import Invoice


@shared_task
def check_overdue_invoices():

    now_date = timezone.now()
    overdue_invoices = Invoice.objects.filter(
        payment_date__isnull=True, payment_due_date__lt=now_date
    )

    for invoice in overdue_invoices:
        redis_key = f"invoice:{invoice.id}:to-notifie"

        if (
            not redis_client.get(redis_key)
            and invoice.outstanding_unpaid(now_date)
            and not invoice.sended_overdude_notification_at
        ):
            redis_client.set(redis_key, "1", ex=86400 * 2)


@shared_task
def send_overdue_invoice_notification():
    redis_key_pattern = "invoice:*:to-notifie"

    invoice_notification_service = InvoiceNotificationService()

    for key in redis_client.scan_iter(match=redis_key_pattern):
        invoice_id = key.split(":")[1]

        with redis_client.pipeline() as pipe:
            try:
                pipe.watch(key)

                if pipe.get(key) == "1":
                    invoice_notification_service.send_invoice_overdue_notification(
                        invoice_id
                    )

                    updated = Invoice.objects.filter(
                        id=invoice_id, sended_overdude_notification_at=None
                    ).update(sended_overdude_notification_at=timezone.now())

                    if updated:
                        pipe.delete(f"invoice:{invoice_id}:to-notifie")
                    pipe.execute()

            except WatchError:
                continue
            finally:
                redis_client.unwatch()
