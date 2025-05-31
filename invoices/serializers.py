from rest_framework import serializers
from .models import Invoice


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField()


class InvoiceModelSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ("created_at", "updated_at")


class InvoiceElasticsearchSerializer(serializers.Serializer):
    number = serializers.CharField()
    principal_company_name = serializers.CharField()
    reciepient_company_name = serializers.CharField()
    issue_date = serializers.DateTimeField()
    payment_due_date = serializers.DateTimeField()
    payment_date = serializers.DateTimeField(allow_null=True)
    total = serializers.IntegerField()
    description = serializers.CharField()
    products = ProductSerializer(many=True)
