from rest_framework import serializers
from ..models.device_permission_logger_models import *

class DevicePermissionLoggerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField()
    permission = serializers.CharField()
    status = serializers.BooleanField()
    log_at = serializers.DateTimeField(required=False)
    
    class Meta:
        model = DevicePermissionLogger
        fields = ['id', 'user_id', 'permission', 'status', 'log_at']
        
class DevicePermissionLastChangeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField()
    permission = serializers.CharField()
    status_after_change = serializers.BooleanField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    
    class Meta:
        model = DevicePermissionLastChange
        fields = ['id', 'user_id', 'permission', 'status_after_change', 'created_at', 'updated_at']
        
class DevicePermissionsSerializer(serializers.ModelSerializer):
    # id  = serializers.IntegerField(required=False)
    permission_code = serializers.CharField()
    permission_name = serializers.CharField(required=False)
    permission_desc = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    
    class Meta:
        model = DevicePermissions
        fields = ['permission_code', 'permission_name', 'permission_desc', 'is_active']