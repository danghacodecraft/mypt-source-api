from app.myHttp.models.oauth_access_token import OauthAccessToken
from rest_framework.serializers import ModelSerializer

class OauthAccessTokenSerializer(ModelSerializer):
    class Meta:
        model = OauthAccessToken
        fields = '__all__'
