from ..models.kpi_info import KpiInfo
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class KpiInfoSerializer(ModelSerializer):
    class Meta:
        model = KpiInfo
        fields = '__all__'
