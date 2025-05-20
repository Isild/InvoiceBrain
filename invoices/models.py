from django.db import models
from django.utils import timezone

# Create your models here.

class Invoice(models.Model):
    number = models.CharField(max_length=100)
    principal_company_name = models.CharField(max_length=200)
    reciepient_company_name = models.CharField(max_length=200)
    issue_date = models.DateTimeField()
    payment_due_date = models.DateTimeField()
    payment_date = models.DateTimeField(null=True)
    total = models.IntegerField()
    description = models.CharField(max_length=2048, default='')
    products = models.JSONField(default=dict)
    # file = models.FileField(upload_to="invoices/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sended_overdude_notification_at = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return f"Invoice {self.number} - {self.principal_company_name}"

    def was_payed(self):
        return self.payment_date != None
    
    def outstanding_unpaid(self, checking_date = None):
        checking_date = checking_date or timezone.now()

        return bool(self.payment_date) or checking_date > self.payment_due_date

