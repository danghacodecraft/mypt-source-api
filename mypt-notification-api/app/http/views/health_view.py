from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
import json
from datetime import datetime
from django.conf import settings as project_settings
from app.configs import app_settings
from app.core.helpers.auth_session_handler import getUserAuthSessionData
from app.http.entities import global_data
import redis

from app.http.paginations.custom_pagination import StandardPagination


@api_view(["GET"])
def healthCheckBK(request):

    # test lay domain name tu request
    domainName = request.get_host()

    # test ket noi mysql db
    try:
        queryset = Employee.objects.all()
        count = Employee.objects.count()
        paginator = StandardPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = EmployeeSerializer(result, many=True)
        data = {
                'numberPage': count//StandardPagination.page_size+1,
                'newsList': serializer.data
            }
        # print('data ok')
        # print(data)
    except:
        # print('data not ok')
        return Response({'status':0, 'message':'data connection not ok'}, status.HTTP_200_OK)

    # test ket noi redis
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                           , port=project_settings.REDIS_PORT_CENTRALIZED
                                           , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                           , decode_responses=True, charset="utf-8")

    resSetRedisKey = redisInstance.set("profile", "Day la value cua Redis key profile abcdef 123969", 3600)
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

    resSetRedisKey = redisInstance.set("myptNoti","This is value of Redis key myptNoti THANOS OPTION", 3600)
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
            "mysqlConInfo": {
                "host": project_settings.DATABASES['default']['HOST'],
                "port": project_settings.DATABASES['default']['PORT'],
                "dbName": project_settings.DATABASES['default']['NAME'],
                "password": project_settings.DATABASES['default']['PASSWORD']
            },
            "domainName": domainName,
            "redisVal": redisInstance.get("myptNoti"),
            "authUserSession": getUserAuthSessionData(request.headers.get("Authorization"))
        }
    }

    return Response(resData, status.HTTP_200_OK)