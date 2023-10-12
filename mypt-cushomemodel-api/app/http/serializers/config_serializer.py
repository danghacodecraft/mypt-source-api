import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.configs import Configs


class ConfigsSerializer(ModelSerializer):
    configId = serializers.IntegerField(source='config_id')
    configType = serializers.CharField(source='config_type')
    configKey = serializers.CharField(source='config_key')
    configValue = serializers.CharField(source='config_value')
    configDescVI = serializers.CharField(source='config_description_vi')
    configDescEN = serializers.CharField(source='config_description_en')
    configStatus = serializers.CharField(source='config_status')
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Configs
        # fields = '__all__'
        fields = ['configId', 'configType', 'configKey', 'configDescVI', 'configDescEN',
                  'configStatus', 'owner', 'createdAt', 'updatedAt', 'note', 'configValue']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['configValue'] = json.loads(representation['configValue'])
        except Exception as ex:
            print(ex)
            pass
        return representation
