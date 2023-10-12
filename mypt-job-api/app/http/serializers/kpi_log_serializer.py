from app.core.helpers.global_variable import YEAR_month_day, DATETIME_Y_m_d
from app.http.models.kpi_log import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class KpiLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = KpiLog
        fields = '__all__'
