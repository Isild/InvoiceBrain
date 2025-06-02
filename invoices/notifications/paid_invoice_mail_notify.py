from rest_framework import status

from notifications.tasks import send_mail_notification
from shared.exceptions.mail_notification_exceptions import (
    NotificationMailMissingFieldException,
)
from shared.notifications.mail_notify import MailNotify
from utils.logger_helpers import generate_exception_response


class PaidInvoiceMailNotify(MailNotify):
    _valid_message_fields = ["invoice_id", "payment_date"]

    def _generate_message(self, message_data: dict[str, str]) -> str:
        message_data = self._get_valid_message_fields(message_data)

        return f"Invoice with ID: {message_data['invoice_id']} was paid at {message_data['payment_date']}"

    def send(
        self,
        mails: list[str],
        message_data: dict[str, str],
        subject: str = "Invoice payment",
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
                message="Failed to send paid invoice mail notification: Unhandled exception",
                exception=exc,
                path=None,
                request_id=None,
            )
