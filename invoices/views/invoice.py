from rest_framework import viewsets
from notifications.tasks import (send_mail_notification,
                                 send_paid_invoice_notification)
from shared.logging.logger import AppLogger

from ..models import Invoice
from ..serializers import InvoiceSerializer
from ..notifications.new_invoice_mail_notify import NewInvoiceMailNotify
from ..notifications.paid_invoice_mail_notify import PaidInvoiceMailNotify


class InvoiceViewSet(viewsets.ModelViewSet):
    logger = AppLogger()

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def _generate_create_mail_data(self, invoice_id: str) -> dict[str, str]:
        return {
            'invoice_id': invoice_id
        }

    def _generate_update_mail_data(self, invoice_id: str, payment_date: str) -> dict[str, str]:
        return {
            'invoice_id': invoice_id,
            'payment_date': payment_date
        }

    def perform_create(self, serializer):
        invoice = serializer.save()
        # TODO: add dynamic mails
        emails = ['no-reply@invoicebrain.com']
        message_data = self._generate_create_mail_data(invoice.id)

        notify = NewInvoiceMailNotify()
        notify.send(emails, message_data)

    def perform_update(self, serializer):
        old_invoice_payment_date = self.get_object().payment_date

        invoice = serializer.save()

        if invoice.payment_date != old_invoice_payment_date and invoice.payment_date:
            emails = ["email@test.com"]
            message_data = self._generate_update_mail_data(invoice.id, invoice.payment_date)

            notify = PaidInvoiceMailNotify()
            notify.send(emails, message_data)
