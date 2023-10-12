from rest_framework import serializers
from ..models.send_email import *

class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmail
        fields = ['email']