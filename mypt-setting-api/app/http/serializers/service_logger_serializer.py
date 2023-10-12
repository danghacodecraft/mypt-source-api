from rest_framework import serializers
from ..models.service_logger import ServiceLogger


class ServiceLoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLogger
        fields = '__all__'
        
    id = serializers.IntegerField(required=False)
    path = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    data = serializers.DictField(required=False)
    params = serializers.DictField(required=False)
    headers = serializers.DictField(required=False)
    result = serializers.CharField(required=True)
    called_at = serializers.DateTimeField(required=False)