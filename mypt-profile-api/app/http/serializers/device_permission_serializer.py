from rest_framework import serializers
from ..models.device_permission_logger_models import *


class DevicePermissionLoggerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    userId = serializers.IntegerField(source="user_id")
    permission = serializers.CharField()
    status = serializers.BooleanField()
    logAt = serializers.DateTimeField(source="log_at", required=False)

    class Meta:
        model = DevicePermissionLogger
        fields = ['id', 'userId', 'permission', 'status', 'logAt']


class DevicePermissionLastChangeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    userId = serializers.IntegerField(source="user_id")
    permission = serializers.CharField()
    statusAfterChange = serializers.BooleanField(source="status_after_change")
    createdAt = serializers.DateTimeField(source="created_at", required=False)
    updatedAt = serializers.DateTimeField(source="updated_at", required=False)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = DevicePermissionLastChange
        fields = ['id', 'userId', 'permission', 'statusAfterChange', 'createdAt', 'updatedAt']


class DevicePermissionsSerializer(serializers.ModelSerializer):
    # id  = serializers.IntegerField(required=False)
    permissionCode = serializers.CharField(source="permission_code")
    permissionName = serializers.CharField(source="permission_name", required=False)
    permissionDesc = serializers.CharField(source="permission_desc", required=False)
    isActive = serializers.BooleanField(source="is_active", required=False)

    class Meta:
        model = DevicePermissions
        fields = ['permissionCode', 'permissionName', 'permissionDesc', 'isActive']
