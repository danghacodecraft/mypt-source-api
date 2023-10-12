import json
from rest_framework.viewsets import ViewSet
from ...core.helpers.response import *
from ...core.helpers.utils import *
from ...core.entities.redis_service import RedisService


class CacheManagerView(ViewSet):
    cache = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        redis_service = RedisService()
        self.cache = redis_service.redis_service

    def get_all_cache(self, request):
        data = self.cache.keys('*')
        return response_data(data)

    def get_cache_value_by_key(self, request):
        key = request.data.get('key', '')
        if empty(key):
            return response_error(status=5, data={'key': 'requied'})
        value = self.cache.get(key)
        if empty(value):
            return response_data()
        try:
            value = json.loads(value)
        except:
            print('Json load string {}'.format(value))
        return response_data(value)

    def clear_cache_by_key(self, request):
        key = request.data.get('key', '')
        if empty(key):
            return response_error(status=5, data={'key': 'requied'})
        return response_data(self.cache.delete(key))

    def clear_cache_by_prefix(self, request):
        prefix = request.data.get('prefix', '')
        if empty(prefix):
            return response_error(status=5, data={'prefix': 'requied'})
        keys = self.cache.keys(prefix + ':*')
        if len(keys) == 0:
            return response_error(status=5, data={'prefix': 'Not found keys'})
        res = {}
        total = 0
        for key in keys:
            total += 1
            res[key] = self.cache.delete(key)
        return response_data({
            'total_deleted': total,
            'details': res
        })
