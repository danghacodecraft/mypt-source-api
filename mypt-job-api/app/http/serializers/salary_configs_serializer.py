import json

from rest_framework import serializers
from http.models.salary_configs import SalaryConfigs
from core.helpers.global_variable import *
from core.helpers.utils import empty
from core.entities.redis_service import RedisService


class SalaryConfigsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryConfigs
        fields = ['config_key']

    def getContentByKey(_config_key):
        salaryCacheKey = '{}:{}'.format(SALARY_CONFIG_CACHE_KEY_NAME, _config_key)
        cache = RedisService().redis_service
        value = cache.get(salaryCacheKey)
        if not empty(value):
            value = json.loads(value)
        if empty(value):
            data = SalaryConfigs.objects.filter(config_key=_config_key).values('config_value')
            data = list(data)
            if len(data) == 0:
                return None
            value = data[0].get('config_value', '')
            cache.set(salaryCacheKey, json.dumps(value))
        return value
