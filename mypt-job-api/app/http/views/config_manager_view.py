from rest_framework.viewsets import ViewSet
from core.helpers.response import *
from http.serializers.salary_configs_serializer import *


class ConfigManagerView(ViewSet):
    cache = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        redis_service = RedisService()
        self.cache = redis_service.redis_service

    def get_all_configs(self, request):
        data = SalaryConfigs.objects.filter().values('config_key')
        if not empty(data):
            data = [x['config_key'] for x in data]
        return response_data(data)

    def get_config_value_by_key(self, request):
        key = request.data.get('key', '')
        if empty(key):
            return response_error(status=5, data={'key': 'requied'})
        data = SalaryConfigs.objects.filter(config_key=key).values('config_value')
        if len(data) < 1:
            return response_data(5, 'Key not found')

        value = list(data)[0].get('config_value', '{}')
        return response_data(value)

    def update_config_by_key(self, request):
        key = request.data.get('key', '')
        value = request.data.get('value', None)
        note = request.data.get('note', None)
        if empty(key):
            return response_error(status=5, data={'key': 'requied'})
        configObj = SalaryConfigs.objects.filter(config_key=key).first()
        if empty(configObj):
            return response_data(5, 'Key not found')
        if not empty(value):
            configObj.config_value = value
            # xóa cache
            keyCache = SALARY_CONFIG_CACHE_KEY_NAME + ':' + key
            self.cache.delete(keyCache)
        if not empty(note):
            configObj.note = note
        configObj.save()
        return response_data(self.cache.delete(key))
