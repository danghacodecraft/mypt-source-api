from rest_framework import serializers
from ..models.call_api import CallAPILogger


class CallAPILoggerSerializer(serializers.ModelSerializer):
    METHOD_CHOICES = ["get", "post", "put", "patch", "delete", "head"]
    
    class Meta:
        model = CallAPILogger
        fields = '__all__'
        
    id = serializers.IntegerField(required=False)
    url = serializers.CharField(required=True)
    method = serializers.ChoiceField(required=True, choices=METHOD_CHOICES)
    data = serializers.DictField(required=False, allow_null=True, default=None)
    params = serializers.DictField(required=False, allow_null=True, default=None)
    headers = serializers.DictField(required=False, allow_null=True, default=None)
    result = serializers.CharField(required=False, allow_null=True, default=None)
    called_at = serializers.DateTimeField(required=False)