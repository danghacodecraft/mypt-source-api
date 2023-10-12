from rest_framework.viewsets import ViewSet
from django.template.loader import get_template
from ...core.helpers.mail import *
from ...core.helpers.response import *

class SendMailView(ViewSet):
    def send_email(self, request):
        # try:
            message = get_template("text.html").render()
            subject = "Tieu de o day"
            recipient_list = ["phuongnam.duyenntk@fpt.net", ]
            send_email_fpt(subject=subject, message=message, recipient_list=recipient_list)
            return response_data()
        # except Exception as ex:
        #     return response_data(ex)