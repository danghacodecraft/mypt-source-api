from rest_framework import serializers

from core.helpers.utils import *
from http.models.salary_real import SalaryReal
from http.serializers.salary_configs_serializer import SalaryConfigsSerializer
from ...configs import app_settings


class SalaryRealSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source='employee_code')

    class Meta:
        model = SalaryReal
        fields = ['employee_code']

    def getSalaryByMonth(self, _employee_mail, _year, _month):
        responseDefault = {
            'salary_total': "0",
            'salary_details': []
        }
        month = '{:02d}-{}'.format(_month, _year)
        salaryStruct = SalaryConfigsSerializer.getContentByKey('SALARY_REAL_STRUCT')
        if empty(salaryStruct):
            print("[ERROR] SalaryRealSerializer get SALARY_REAL_STRUCT empty")
            return responseDefault
        print(_employee_mail, month)
        importData = SalaryReal.objects.filter(email=_employee_mail, month=month).values()
        if empty(importData) or len(importData) < 1:
            return responseDefault
        values = importData[0]
        # print(values)
        data = getSalaryObjFromDB(_decodeKey=app_settings.SALARY_SECRET_KEY, _value_list=values, _item=salaryStruct)
        if empty(data):
            return responseDefault
        return {
            'salary_total': data.get('number', '0'),
            'salary_details': data.get('details', [])
        }
