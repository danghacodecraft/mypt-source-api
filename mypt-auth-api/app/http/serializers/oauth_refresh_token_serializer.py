from app.http.models.oauth_refresh_token import OauthRefreshToken
from rest_framework.serializers import ModelSerializer

class OauthRefreshTokenSerializer(ModelSerializer):
    class Meta:
        model = OauthRefreshToken
        fields = '__all__'
