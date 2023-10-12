from app.myHttp.models.sender_tokens import *
from rest_framework.serializers import ModelSerializer

class SenderTokensSerializer(ModelSerializer):
    class Meta:
        model = SenderTokens
        fields = '__all__'
