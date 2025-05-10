from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Invoice

invoice_index = Index('invoices')

@registry.register_document
class InvoiceDocument(Document):
    class Index:
        name = 'invoices'

    class Django:
        model = Invoice
        fields = [
            'number',
            'principal_company_name',
            'reciepient_company_name',
            'issue_date',
            'payment_due_date',
            'payment_date',
            'total',
            'created_at',
            'updated_at',
        ]
 