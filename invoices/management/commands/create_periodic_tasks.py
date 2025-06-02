from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule

from shared.logging.logger import AppLogger
from utils.tasks import create_periodic_task


class Command(BaseCommand):
    logger = AppLogger()

    help = "Create/update periodic Celery tasks for the project."

    def handle(self, *args, **options):
        create_periodic_task(
            task_name="Check overdue invoices",
            task_path="invoices.tasks.check_overdue_invoices",
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        create_periodic_task(
            task_name="Send overdue invoices notifications",
            task_path="invoices.tasks.send_overdue_invoice_notification",
            every=2,
            period=IntervalSchedule.MINUTES,
        )

        self.stdout.write(self.style.SUCCESS("Periodic tasks created."))
