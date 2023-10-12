from app.myHttp.models.oauth_auth_code import OauthAuthCode
from rest_framework.serializers import ModelSerializer

class OauthAuthCodeSerializer(ModelSerializer):
    class Meta:
        model = OauthAuthCode
        fields = '__all__'
