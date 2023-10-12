from app.http.models.permission_group import *
from rest_framework.serializers import ModelSerializer

class PermissionGroupSerializer(ModelSerializer):
    class Meta:
        model = PermissionGroup
        fields = '__all__'
