from app.http.models.user_senders import *
from rest_framework.serializers import ModelSerializer

class UserSendersSerializer(ModelSerializer):
    class Meta:
        model = UserSenders
        fields = '__all__'
