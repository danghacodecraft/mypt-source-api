import redis
from rest_framework.viewsets import ViewSet

from core.entities.redis_service import RedisService
from core.helpers.response import *
from core.helpers.utils import *


class CacheManagerView(ViewSet):
    cache = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        redis_service = RedisService()
        self.cache = redis_service.redis_service

    def get_all_cache(self, request):
        redis_client = redis.StrictRedis(
            host=project_settings.REDIS_HOST_CENTRALIZED,
            port=project_settings.REDIS_PORT_CENTRALIZED,
            db=request.data['database'],
            password=project_settings.REDIS_PASSWORD_CENTRALIZED,
            decode_responses=True,
            charset="utf-8"
        )
        data = [item.split(':') for item in redis_client.keys('*')]
        cache_key = {}
        for item in data:
            if item[0] not in cache_key:
                cache_key[item[0]] = [':'.join(item[1:])]
            else:
                cache_key[item[0]].append(':'.join(item[1:]))
        return response_data(cache_key)

    def get_all_cache_key(self, request):
        db_key = {}
        for db_num in range(0, 16):  # 16 cơ sở dữ liệu từ 0 đến 15
            redis_client = redis.StrictRedis(
                host=project_settings.REDIS_HOST_CENTRALIZED,
                port=project_settings.REDIS_PORT_CENTRALIZED,
                db=db_num,
                password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                decode_responses=True,
                charset="utf-8"
            )
            keys = redis_client.keys('*', db=db_num)
            data = [item.split(':') for item in keys]
            cache_key = {}
            for item in data:
                print(item)
                if item[0] not in cache_key:
                    cache_key[item[0]] = [':'.join(item[1:])]
                else:
                    cache_key[item[0]].append(':'.join(item[1:]))
            db_key[f'redis_db{db_num}'] = cache_key
        return response_data(db_key)

    def clear_db_cache(self, request):
        redis_client = redis.StrictRedis(
            host=project_settings.REDIS_HOST_CENTRALIZED,
            port=project_settings.REDIS_PORT_CENTRALIZED,
            db=request.GET['database'],
            password=project_settings.REDIS_PASSWORD_CENTRALIZED,
            decode_responses=True,
            charset="utf-8"
        )
        redis_client.flushdb()
        return response_data(message='Clear cache successfully!')
