from rest_framework import viewsets

from notifications.tasks import (send_new_invoice_notification,
                                 send_paid_invoice_notification)

from ..models import Invoice
from ..serializers import InvoiceSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def perform_create(self, serializer):
        invoice = serializer.save()
        send_new_invoice_notification.delay("email@test.com", invoice.id)

    def perform_update(self, serializer):
        old_invoice_payment_date = self.get_object().payment_date

        invoice = serializer.save()

        if invoice.payment_date != old_invoice_payment_date and invoice.payment_date:
            send_paid_invoice_notification.delay("email@test.com", invoice.id, invoice.payment_date)
