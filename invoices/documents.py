from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Invoice

invoice_index = Index('invoices')

@registry.register_document
class InvoiceDocument(Document):
    ELASTIC_ALLOWED_SEARCH_FIELDS = {
        'issue_date',
        'payment_due_date',
        'payment_date',
        'created_at',
        'updated_at',
    }

    products = fields.NestedField(
        properties={
            'name': fields.TextField(),
            'price': fields.IntegerField(),
        }
    )
    description = fields.TextField()

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

    # # TODO: add error handling when wrong data structure
    def prepare_products(self, instance):
        return [
            {
                'name': p.get('name', ''),
                'price': int(p.get('price', 0))
            }
            for p in instance.products or []
            if isinstance(p, dict)
        ]
