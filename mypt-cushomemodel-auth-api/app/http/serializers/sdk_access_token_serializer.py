from app.http.models.sdk_access_token import SdkAccessToken
from rest_framework.serializers import ModelSerializer

class SdkAccessTokenSerializer(ModelSerializer):
    class Meta:
        model = SdkAccessToken
        fields = '__all__'
