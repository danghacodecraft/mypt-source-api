from rest_framework import serializers
from ..models.setting_config_model import *
        
class SettingConfigSerializer(serializers.ModelSerializer):
    config_type = serializers.CharField(required=False)
    config_key = serializers.CharField(required=True)
    config_value = serializers.CharField(required=True)
    config_description_vi = serializers.CharField(required=False)
    config_description_en = serializers.CharField(required=False)
    config_status = serializers.CharField(required=False)
    owner = serializers.CharField(required=False)
    date_created = serializers.DateTimeField(required=False)
    date_last_updated = serializers.DateTimeField(required=False)
    note = serializers.CharField(required=False)
    
    class Meta:
        model = SettingConfig
        fields = '__all__'