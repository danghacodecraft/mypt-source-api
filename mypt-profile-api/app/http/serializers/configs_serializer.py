from rest_framework import serializers

from ..models.configs import *


class ProfileConfigSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='config_id')
    configKey = serializers.CharField(source='config_key')
    configValue = serializers.CharField(source='config_value')
    # createdAt = serializers.DateTimeField(source='created_at')
    # lastModifiedAt = serializers.DateTimeField(source='last_modified_at')

    class Meta:
        model = ProfileConfig
        fields = ['configKey', 'configValue']

    def get_value_by_key(self):
        data = ProfileConfig.objects.filter(config_key=self).values('config_value')
        data = list(data)

        if len(data) == 0:
            return None
        value = data[0].get('config_value', '')
        return value
