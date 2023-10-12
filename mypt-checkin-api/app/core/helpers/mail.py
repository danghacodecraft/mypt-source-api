from django.core.mail import send_mail
from django.conf import settings

def send_email_fpt(subject="", message="", recipient_list=[]):
    email_from = settings.EMAIL_HOST_USER
    send_mail( subject=subject, message=message, html_message=message, from_email=email_from, recipient_list=recipient_list)