from rest_framework import serializers
from ..models.setting_model import *


class SettingSerializer(serializers.ModelSerializer):
    configKey = serializers.CharField(source='config_key')
    configValue = serializers.CharField(source='config_value')
    # configDescriptionVNI = serializers.CharField(source='config_description_vi')
    # configDescriptionENG = serializers.CharField(source='config_description_en')
    # configID = serializers.IntegerField(source='config_id')
    # configType = serializers.CharField(source='config_type')
    # configStatus = serializers.CharField(source='config_status')
    # dateCreated = serializers.DateTimeField(source='date_created')
    # dateLastUpdated = serializers.DateTimeField(source='date_last_updated')

    class Meta:
        model = Setting
        fields = ['configKey', 'configValue']
        
class SettingConfigSerializer(serializers.ModelSerializer):
    # config_id = models.BigAutoField(primary_key=True)
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
        model = Setting
        fields = '__all__'