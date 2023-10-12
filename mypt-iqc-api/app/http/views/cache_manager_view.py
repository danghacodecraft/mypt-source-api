import ast
from datetime import datetime
from rest_framework.viewsets import ViewSet
from core.entities.redis_service import RedisService
from core.helpers import global_variable, iqc_global_variable
from core.helpers.response import response_data
from core.helpers import utils


class CacheManagerView(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        redis_service = RedisService()
        self.cache = redis_service.redis_service

    def get_all_cache(self, request):
        try:
            data = self.cache.keys('*')
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_all_cache >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)

    def get_cache_value_by_key(self, request):
        data = request.data.copy()
        try:
            if "key" not in data:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="key là bắt buộc!")

            key = data["key"]
            iqc_config_str = self.cache.get(key)
            if iqc_config_str is None:
                return response_data(status=global_variable.STATUS_CODE_NO_DATA,
                                     message="Không tìm thấy key!")
            iqc_config = ast.literal_eval(iqc_config_str)

            return response_data(data=iqc_config)
        except Exception as ex:
            print(f"{datetime.now()} >> get_cache_value_by_key >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)

    def clear_cache_by_key(self, request):
        data = request.data.copy()
        try:
            if "key" not in data:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="key là bắt buộc!")

            key = data["key"]
            iqc_config_str = self.cache.get(key)
            if iqc_config_str is None:
                return response_data(status=global_variable.STATUS_CODE_NO_DATA,
                                     message="Không tìm thấy key!")
            self.cache.delete(key)
            return response_data()
        except Exception as ex:
            print(f"{datetime.now()} >> clear_cache_by_key >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)

    def clear_cache_by_prefix(self, request):
        try:
            prefix = request.data.get('prefix', '')
            if utils.empty(prefix):
                return response_data(status=5, data={'prefix': 'requied'}, message="prefix là bắt buộc!")
            keys = self.cache.keys(prefix + ':*')
            if len(keys) == 0:
                return response_data(status=5, data={'prefix': 'Not found keys'}, message="Không tìm thấy keys này!")
            res = {}
            total = 0
            for key in keys:
                total += 1
                res[key] = self.cache.delete(key)
            return response_data({
                'total_deleted': total,
                'details': res
            })
        except Exception as ex:
            print(f"{datetime.now()} >> clear_cache_by_prefix >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)

