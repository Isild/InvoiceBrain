from celery import shared_task
from django.core.mail import send_mail

# TODO: add dynamic mail, from redis config
SUPPORT_MAIL = 'no-reply@invoicebrain.com'


@shared_task
def send_mail_notification(emails, subject, message):
    send_mail(subject, message, SUPPORT_MAIL, emails)

@shared_task
def send_new_invoice_notification(email, invoice_id):
    subject = "New invoice"
    message = f"New invoice occured with ID: {invoice_id}."

    send_mail(subject, message, 'no-reply@invoicebrain.com', [email])

@shared_task
def send_paid_invoice_notification(email, invoice_id, payment_date):
    subject = "Invoice payment"
    message = f"Invoice with ID: {invoice_id} was paid at {payment_date}"

    send_mail(subject, message, 'no-reply@invoicebrain.com', [email])
