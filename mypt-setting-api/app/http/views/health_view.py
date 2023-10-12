# from rest_framework.decorators import api_view
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.core.helpers.auth_session_handler import getUserAuthSessionData
from core.helpers.response import response_data
from rest_framework.viewsets import ViewSet
from django.conf import settings as project_settings
import redis
from core.helpers.response import response_data


class SettingHealthCheckView(ViewSet):

    def getHealthCheck(self, request):
        # resData = {
        #     "domainName": request.get_host(),
        #     "notiMessage": "Service worked",
        #     "employeeName": "NGUYEN THI THANH BINH",
        #     "empJobTile": "Can bo xu ly su co"
        # }
        # return response_data(resData)

        resData = {
            "set_attributes": {
                "employeeName": "NGUYEN THI THANH BINH",
                "empJobTile": "Can bo xu ly su co"
            }
        }

        return Response(resData, status.HTTP_200_OK)

    def testGetUserSession(self, request):
        # test lay domain name tu request
        domainName = request.get_host()

        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("myptSettingPhong", "That is value of Redis key myptSetting SUPER CAT",
                                           3600)

        resData = {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "domainName": domainName,
            "myptSettingRedisValue": redisInstance.get("myptSettingPhong"),
            "authUserSession": getUserAuthSessionData(request.headers.get("Authorization"))
        }

        return response_data(resData, 1, "Get user session success")