from ..models.sdk_users import SdkUsers
from rest_framework.serializers import ModelSerializer

class SdkUsersSerializer(ModelSerializer):
    class Meta:
        model = SdkUsers()
        fields = '__all__'
