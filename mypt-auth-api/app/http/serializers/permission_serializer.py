from app.myHttp.models.permission_model import *
from rest_framework.serializers import ModelSerializer

class PermissionSerializer(ModelSerializer):
    class Meta:
        model = PermissionModel
        fields = '__all__'
