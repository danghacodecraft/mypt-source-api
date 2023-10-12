from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as project_settings
from app.http.entities import global_data
import redis


@api_view(["GET"])
def healthCheckBK(request):

    # test lay domain name tu request
    domainName = request.get_host()

    # test ket noi redis
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                           , port=project_settings.REDIS_PORT_CENTRALIZED
                                           , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                           , decode_responses=True, charset="utf-8")

    redisInstance.set("profile", "Day la value cua Redis key profile abcdef 123969", 3600)
    # print("redis value : " + redisInstance.get("profile"))
    # print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
    # print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
    # print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

    resData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "testRedisVal": redisInstance.get("profile"),
            "domainName": domainName
        }
    }

    return Response(resData, status.HTTP_200_OK)

@extend_schema(
        operation_id='API kiểm tra sức khỏe service',
        summary='API kiểm tra sức khỏe service',
        tags=["4. API kiểm tra sức khỏe service"],
        description='API kiểm tra sức khỏe service',
        responses={
            status.HTTP_200_OK: None
        }
    )
@api_view(["GET"])
def healthCheck(request):
    # test lay domain name tu request
    domainName = request.get_host()

    # test ket noi redis
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                      , port=project_settings.REDIS_PORT_CENTRALIZED
                                      , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                      password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                      , decode_responses=True, charset="utf-8")

    redisInstance.set("myptNoti","This is value of Redis key myptNoti THANOS OPTION", 3600)
    # print("redis value of myptNoti : " + redisInstance.get("myptNoti"))

    resData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "domainName": domainName,
            "redisVal": redisInstance.get("myptNoti"),
            "authUserSession": global_data.authUserSessionData
        }
    }

    return Response(resData, status.HTTP_200_OK)