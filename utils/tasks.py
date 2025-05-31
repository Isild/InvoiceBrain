from typing import Literal

from django.db.utils import OperationalError, ProgrammingError
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from shared.logging.logger import AppLogger

logger = AppLogger()

Period = Literal[
    IntervalSchedule.DAYS,
    IntervalSchedule.HOURS,
    IntervalSchedule.MINUTES,
    IntervalSchedule.SECONDS,
    IntervalSchedule.MICROSECONDS,
]


def create_periodic_task(
    task_name: str, task_path: str, every: int, period: Period
) -> bool:
    """
    Creates or updates a periodic Celery task.

    Logs exceptions on database access failures.

    Args:
        name: Name of the task.
        task: Full dotted path to Celery task.
        every: Frequency of execution.
        period: Unit of time (e.g., 'minutes', 'hours').
    """
    try:
        schedule, _ = IntervalSchedule.objects.update_or_create(
            every=every + 1, period=period
        )

        PeriodicTask.objects.update_or_create(
            interval=schedule, name=task_name + "dupa", task=task_path
        )

        return True
    except (OperationalError, ProgrammingError) as exception:
        logger.log_exception(
            feature=f"CeleryTask:{task_path}",
            message="Unhandled exception",
            exception=exception,
            path=None,
            request_id=None,
        )

        return False
