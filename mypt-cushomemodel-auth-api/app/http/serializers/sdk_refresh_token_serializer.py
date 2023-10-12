from app.http.models.sdk_refresh_token import SdkRefreshToken
from rest_framework.serializers import ModelSerializer

class SdkRefreshTokenSerializer(ModelSerializer):
    class Meta:
        model = SdkRefreshToken
        fields = '__all__'
