from rest_framework import viewsets
from shared.logging.logger import AppLogger

from ..models import Invoice
from ..serializers import InvoiceModelSerializer
from ..services.invoice_notifications import InvoiceNotificationService


class InvoiceViewSet(viewsets.ModelViewSet):
    logger = AppLogger()

    queryset = Invoice.objects.all()
    serializer_class = InvoiceModelSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.invoice_notification_service = InvoiceNotificationService()

    def perform_create(self, serializer):
        invoice = serializer.save()
        self.invoice_notification_service.send_invoice_created_notification(invoice)

    def perform_update(self, serializer):
        old_invoice_payment_date = self.get_object().payment_date

        invoice = serializer.save()

        if invoice.payment_date != old_invoice_payment_date and invoice.payment_date:
            self.invoice_notification_service.send_invoice_paid_notification(invoice)
