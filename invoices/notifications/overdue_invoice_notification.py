from notifications.tasks import send_mail_notification
from utils.logger_helpers import generate_exception_response
from rest_framework import status

from shared.exceptions.mail_notification_exceptions import NotificationMailMissingFieldException
from shared.notifications.mail_notify import MailNotify


class OverdueInvoiceMailNotify(MailNotify):
    _valid_message_fields = [
        'invoice_id',
    ]

    def _generate_message(self, message_data: dict[str, str]) -> str:
        message_data = self._get_valid_message_fields(message_data)

        return f"Invoice is overdue, ID: {message_data['invoice_id']}."

    def send(self, mails: list[str], message_data: dict[str, str], subject: str = "Overdue") -> None:
        message = self._generate_message(message_data)

        try:
            send_mail_notification(emails=mails, subject=subject, message=message)
        except NotificationMailMissingFieldException as exc:
            self.logger.log_exception(
                feature=exc.feature,
                message=exc.message,
                exception=exc,
                path=None,
                request_id=None
            )

            return generate_exception_response({
                'message': exc.message
            }, status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as exc:
            self.logger.log_exception(
                feature="DRFExceptionHandler",
                message="Failed to send overdue invoice mail notification: Unhandled exception",
                exception=exc,
                path=None,
                request_id=None
            )
