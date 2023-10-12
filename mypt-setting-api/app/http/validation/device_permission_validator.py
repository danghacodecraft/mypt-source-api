from rest_framework import serializers
from ..models.device_permission_logger_models import *

class DevicePermissionLoggerValidator(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    permission = serializers.CharField(required=True)
    status = serializers.BooleanField(required=True)

        
class DevicePermissionLastChangeValidator(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    permission = serializers.CharField(required=True)
    status_after_change = serializers.BooleanField(required=True)
    # updated_at = serializers.DateTimeField(required=True)

        
class DevicePermissionsValidator(serializers.Serializer):
    permission_code = serializers.CharField(required=True)

