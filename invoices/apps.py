from django.apps import AppConfig
from django.core.exceptions import ValidationError

class InvoicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoices'


    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError
        from django_celery_beat.models import IntervalSchedule, PeriodicTask
        import invoices.documents 

        try:
            schedule_check_overdude_invoices, _ = IntervalSchedule.objects.update_or_create(
                every=1,
                period=IntervalSchedule.MINUTES
            )

            PeriodicTask.objects.update_or_create(
                interval=schedule_check_overdude_invoices,
                name="Check overdue invoices",
                task="invoices.tasks.check_overdue_invoices"
            )
        except (OperationalError, ProgrammingError):
            pass
        
        try:
            schedule_send_overdude_invoices_notifications, _ = IntervalSchedule.objects.update_or_create(
                every=2,
                period=IntervalSchedule.MINUTES
            )
            PeriodicTask.objects.update_or_create(
                interval=schedule_send_overdude_invoices_notifications,
                name="Send overdue invoices notifications",
                task="invoices.tasks.send_overdude_invoide_notification"
            )
        except (OperationalError, ProgrammingError):
            pass

        return super().ready()
