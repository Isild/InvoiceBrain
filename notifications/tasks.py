from celery import shared_task
from django.core.mail import send_mail

# TODO: add dynamic mail, from redis config
SUPPORT_MAIL = 'no-reply@invoicebrain.com'


@shared_task
def send_mail_notification(emails, subject, message):
    send_mail(subject, message, SUPPORT_MAIL, emails)
