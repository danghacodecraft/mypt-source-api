from app.core.helpers.global_variable import YEAR_month_day, DATETIME_Y_m_d
from app.http.models.kpi import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class KpiSerializer(serializers.ModelSerializer):
    empCode = serializers.CharField(source='emp_code')
    accountMbn = serializers.CharField(source='account_mbn')
    status = serializers.CharField(allow_blank=True, allow_null=True)
    kpiType = serializers.CharField(source='kpi_type')
    timeComplete = serializers.DateTimeField(input_formats=DATETIME_Y_m_d, allow_null=True, source='time_complete')
    timeStartCl1 = serializers.DateTimeField(input_formats=DATETIME_Y_m_d, allow_null=True, source='time_start_cl1')
    timeCompleteCl1 = serializers.DateTimeField(input_formats=DATETIME_Y_m_d, allow_null=True, source='time_complete_cl1')
    timeStartCl2 = serializers.DateTimeField(input_formats=DATETIME_Y_m_d, allow_null=True, source='time_start_cl2')
    timeCompletePtc = serializers.DateTimeField(input_formats=DATETIME_Y_m_d, allow_null=True, source='time_complete_ptc')
    kpiDate = serializers.DateField(source='kpi_date', input_formats=YEAR_month_day, required=True)

    class Meta:
        model = Kpi
        fields = ['empCode',
                  'accountMbn',
                  'contract',
                  'status',
                  'kpiType',
                  'timeComplete',
                  'timeStartCl1',
                  'timeCompleteCl1',
                  'timeStartCl2',
                  'timeCompletePtc',
                  'kpiDate']
