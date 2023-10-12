from rest_framework import serializers
from ..models.cron_model import Cron

class  CronSerializer(serializers.ModelSerializer):
    METHOD_CHOICES = ["get", "post", "put", "patch", "delete", "head"]
    
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    method = serializers.ChoiceField(required=True, choices=METHOD_CHOICES)
    url = serializers.CharField(required=True)
    headers = serializers.DictField(required=False, default=None)
    data = serializers.DictField(required=False, default=None)
    params = serializers.DictField(required=False, default=None)
    proxies = serializers.DictField(required=False, default=None)
    schedule = serializers.CharField(required=True)
    error_schedule = serializers.CharField(required=False, default=None)
    created_at = serializers.DateTimeField(required=False)
    deleted_at = serializers.DateTimeField(required=False)
    
    class Meta:
        model = Cron
        fields = '__all__'