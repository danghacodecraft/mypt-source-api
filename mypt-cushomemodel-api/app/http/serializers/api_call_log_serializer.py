from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.api_call_log import ApiCallLog
from core.helpers.my_datetime import getFormatDatetimeNow


class ApiCallLogSerializer(ModelSerializer):
    apiUrl = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='api_url')
    apiEnv = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='api_env')
    apiInput = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='api_input')
    apiOutput = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='api_output')
    deviceId = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='device_id')
    deviceName = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='device_name')
    deviceToken = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='device_token')
    devicePlatform = serializers.CharField(required=False, allow_null=True, allow_blank=True, source='device_platform')
    sdkUserId = serializers.CharField(required=False, source='sdk_user_id')
    appId = serializers.CharField(required=False, source='app_id')
    sdkAccUsername = serializers.CharField(required=False, source='sdk_acc_username')
    dateCalled = serializers.CharField(required=False, source='date_called')

    class Meta:
        model = ApiCallLog
        fields = ['id', 'apiUrl', 'apiEnv', 'apiInput', 'apiOutput', 'deviceId', 'deviceName', 'deviceToken',
                  'devicePlatform', 'sdkUserId', 'appId', 'sdkAccUsername', 'dateCalled']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def create(self, validated_data):
        validated_data['date_called'] = getFormatDatetimeNow()
        instance = ApiCallLog.objects.create(**validated_data)
        return validated_data
