from ..factories.invoice_notify_factory import InvoiceNotifyFactory
from ..models import Invoice

EMAIL_TO_NOTIFY = "no-reply@invoicebrain.com"


class InvoiceNotificationService:
    def __init__(self, invoice_notification_factory: InvoiceNotifyFactory = None):
        self.invoice_notification_factory = (
            invoice_notification_factory or InvoiceNotifyFactory()
        )

    def _generate_create_mail_data(self, invoice_id: str) -> dict[str, str]:
        return {"invoice_id": invoice_id}

    def _generate_update_mail_data(
        self, invoice_id: str, payment_date: str
    ) -> dict[str, str]:
        return {"invoice_id": invoice_id, "payment_date": payment_date}

    def _generate_overdue_mail_data(self, invoice_id: str) -> dict[str, str]:
        return {"invoice_id": invoice_id}

    # TODO: add dynamics mail notifications
    def send_invoice_created_notification(self, invoice: Invoice) -> None:
        emails = [EMAIL_TO_NOTIFY]
        message_data = self._generate_create_mail_data(invoice.id)

        notifier = self.invoice_notification_factory.create("new")
        notifier.send(emails, message_data)

    def send_invoice_paid_notification(self, invoice: Invoice) -> None:
        emails = [EMAIL_TO_NOTIFY]
        message_data = self._generate_update_mail_data(invoice.id, invoice.payment_date)

        notifier = self.invoice_notification_factory.create("paid")
        notifier.send(emails, message_data)

    def send_invoice_overdue_notification(self, invoice_id: str) -> None:
        emails = [EMAIL_TO_NOTIFY]
        message_data = self._generate_overdue_mail_data(invoice_id)

        notifier = self.invoice_notification_factory.create("overdue")
        notifier.send(emails, message_data)
