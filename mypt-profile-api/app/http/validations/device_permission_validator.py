from rest_framework import serializers
from ..models.device_permission_logger_models import *

class DevicePermissionLoggerValidator(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    permission = serializers.CharField(required=True)
    status = serializers.BooleanField(required=True)

        
class DevicePermissionLastChangeValidator(serializers.Serializer):
    userId = serializers.IntegerField(source="user_id", required=True)
    permission = serializers.CharField(required=True)
    statusAfterChange = serializers.BooleanField(source="status_after_change", required=True)
    # updated_at = serializers.DateTimeField(required=True)

        
class DevicePermissionsValidator(serializers.Serializer):
    permissionCode = serializers.CharField(required=True)

