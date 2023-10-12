from app.http.models.permission_with_route import *
from rest_framework.serializers import ModelSerializer

class PermissionWithRouteSerializer(ModelSerializer):
    class Meta:
        model = PermissionWithRoute
        fields = '__all__'
