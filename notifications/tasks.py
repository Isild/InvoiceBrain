from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_invoice_notification(email, invoice_id):
    subject = "New invoice"
    message = f"New invoice occured with ID: {invoice_id}"

    send_mail(subject, message, 'no-reply@invoicebrain.com', [email])

    print("##################################### send email " + email + " " + message)