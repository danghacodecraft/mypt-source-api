from rest_framework import serializers
from ..models.salary_real_time import *


class SalaryRealTimeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SalaryRealTime
        # 'created_at','updated_at', deleted_at
        fields = ['SumSalaryMonth']
