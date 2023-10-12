from rest_framework import serializers
from http.models.iqc_config import IqcConfig


class IqcConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = IqcConfig
        fields = ['config_key', 'config_value']
