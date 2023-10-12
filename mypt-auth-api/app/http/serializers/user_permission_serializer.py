from app.myHttp.models.user_permission import *
from rest_framework.serializers import ModelSerializer

class UserPermissionSerializer(ModelSerializer):
    class Meta:
        model = UserPermission
        fields = '__all__'
