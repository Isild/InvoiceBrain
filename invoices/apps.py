from django.apps import AppConfig
from django.core.exceptions import ValidationError

class InvoicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoices'


    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError
        from django_celery_beat.models import IntervalSchedule, PeriodicTask
        from utils.tasks import create_periodic_task
        import invoices.documents 

        create_periodic_task(
            task_name="Check overdue invoices",
            task_path="invoices.tasks.check_overdue_invoices",
            every=1,
            period=IntervalSchedule.MINUTES
        )

        create_periodic_task(
            task_name="Send overdue invoices notifications",
            task_path="invoices.tasks.send_overdue_invoice_notification",
            every=2,
            period=IntervalSchedule.MINUTES
        )

        return super().ready()
