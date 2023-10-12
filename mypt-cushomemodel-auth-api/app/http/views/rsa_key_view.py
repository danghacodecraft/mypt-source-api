import json

import redis
from rest_framework.viewsets import ModelViewSet
from django.conf import settings as project_settings

from ..models.rsa_key import RSAKey
from ..serializers.rsa_key_serializer import RSAKeySerializer
from ..validation.rsa_key_validation import RSAKeyCreateValidate
from core.helpers.response import *


class CusHomeModelRSAView(ModelViewSet):

    # Ham nay dung de goi private. Ham nay de luu cac cap Public Key - Private Key cua cac app vao Redis
    def cache_apps_rsa_keys(self, request):
        appsQs = RSAKey.objects.all()
        appsSer = RSAKeySerializer(appsQs, many=True)
        appsArr = appsSer.data
        appsRSAKeysData = {}
        for appItem in appsArr:
            appsRSAKeysData[appItem["appId"]] = {
                "publicKey": appItem["publicKey"],
                "privateKey": appItem["privateKey"]
            }

        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        resSaveRedis = redisInstance.set("appsRSAKeys", str(appsRSAKeysData))

        return response_data({
            "resSaveRedis": resSaveRedis,
            "appsRSAKeys": appsRSAKeysData
        })

    # def list(self, request, *args, **kwargs):
    #     # Đầu tiên, gọi phương thức gốc của lớp cha để lấy dữ liệu
    #     response = super().list(request, *args, **kwargs)
    #
    #     # tạo thông tin lưu redis
    #     data = RSAKey.objects.all()
    #     serializer = RSAKeySerializer(data, many=True)
    #     # result = map(lambda x: dict(x), serializer.data)
    #
    #     # redis
    #     redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
    #                                        , port=project_settings.REDIS_PORT_CENTRALIZED
    #                                        , db=project_settings.REDIS_DATABASE_CENTRALIZED,
    #                                        password=project_settings.REDIS_PASSWORD_CENTRALIZED
    #                                        , decode_responses=True, charset="utf-8")
    #     for item in serializer.data:
    #         redis_instance.set(f'{"appKey"}:{item["appId"]}', json.dumps(item))
    #     return response_data(response.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            app_id = self.request.GET['data']
            data = RSAKey.objects.get(app_id=app_id)
            serializer = RSAKeySerializer(data, many=False)
        except Exception as ex:
            print(str(ex))
            return response_data(message='Dữ liệu không tồn tại', status=0)
        return response_data(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            post_data = request.data
            serializer = RSAKeyCreateValidate(data=post_data)
            if serializer.is_valid():
                serializer.save()

            # tạo thông tin lưu redis
            data = RSAKey.objects.all()
            serializer = RSAKeySerializer(data, many=True)
        except Exception as ex:
            print(str(ex))
            return response_data(message=str(ex), status=0)
        return response_data(serializer.data)

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        try:
            app_id = self.request.GET['data']
            data = RSAKey.objects.get(app_id=app_id)
            data.delete()
            serializer = RSAKeySerializer(data, many=False)

            # redis
            redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")
            redis_instance.delete(f'{"appKey"}:{app_id}')
        except Exception as ex:
            print(str(ex))
            return response_data(message='Dữ liệu không tồn tại', status=0)
        return response_data(serializer.data)
