from rest_framework import serializers
from .models import Invoice


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField()


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

    number = serializers.CharField()
    principal_company_name = serializers.CharField()
    reciepient_company_name = serializers.CharField()
    issue_date = serializers.DateTimeField()
    payment_due_date = serializers.DateTimeField()
    payment_date = serializers.DateTimeField(allow_null=True)
    total = serializers.IntegerField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    products = ProductSerializer(many=True)

    def to_representation(self, instance):
        if hasattr(instance, "to_dict"):
            data = instance.to_dict()
        elif isinstance(instance, dict):
            data = instance
        else:
            data = {
                'number': instance.number,
                'principal_company_name': instance.principal_company_name,
                'reciepient_company_name': instance.reciepient_company_name,
                'issue_date': instance.issue_date,
                'payment_due_date': instance.payment_due_date,
                'payment_date': instance.payment_date,
                'total': instance.total,
                'description': instance.description,
                'created_at': instance.created_at,
                'updated_at': instance.updated_at,
                'products': instance.products or [],
            }

        return super().to_representation(data)
