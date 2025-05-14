from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.db.utils import OperationalError, ProgrammingError

class Command(BaseCommand):
    help = "Create/update periodic Celery tasks for the project."

    def handle(self, *args, **options):
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

        self.stdout.write(self.style.SUCCESS("Periodic tasks created."))
