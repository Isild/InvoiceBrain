from rest_framework import status

from notifications.tasks import send_mail_notification
from utils.logger_helpers import generate_exception_response

from ..exceptions.mail_notification_exceptions import (
    NotificationMailMissingFieldException,
)
from .notify import Notify


class MailNotify(Notify):
    _valid_message_fields = ["message"]

    def _get_valid_message_fields(
        self, fields_to_check: dict[str, str]
    ) -> dict[str, str]:
        missing = [
            field
            for field in self._valid_message_fields
            if field not in fields_to_check
        ]

        if missing:
            raise NotificationMailMissingFieldException(
                message=f"Missing required fields: {', '.join(missing)}",
                feature=MailNotify.__class__.__name__,
                details=fields_to_check,
            )

        return {
            key: fields_to_check[key]
            for key in self._valid_message_fields
            if key in fields_to_check
        }

    def _generate_message(self, message_data: dict[str, str]) -> str:
        return message_data["message"]

    def send(
        self,
        mails: list[str],
        message_data: dict[str, str],
        subject: str = "Mail Notification",
    ) -> None:
        message = self._generate_message(message_data)

        try:
            send_mail_notification(emails=mails, subject=subject, message=message)
        except NotificationMailMissingFieldException as exc:
            self.logger.log_exception(
                feature=exc.feature,
                message=exc.message,
                exception=exc,
                path=None,
                request_id=None,
            )

            return generate_exception_response(
                {"message": exc.message}, status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except Exception as exc:
            self.logger.log_exception(
                feature="DRFExceptionHandler",
                message="Failed to send mail notification: Unhandled exception",
                exception=exc,
                path=None,
                request_id=None,
            )
