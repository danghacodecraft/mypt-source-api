from rest_framework import serializers

class UpdateDeviceTokenValidate(serializers.Serializer):
    device_token = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    device_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    device_platform = serializers.CharField(required=False, allow_blank=True, allow_null=True)