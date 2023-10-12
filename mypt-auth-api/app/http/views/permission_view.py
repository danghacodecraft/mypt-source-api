from rest_framework.decorators import api_view
from http.helpers.response import *
import jwt
import ast
import json
from django.conf import settings as project_settings
from app.configs import app_settings
from app.core.helpers import utils as utHelper
from ..models.permission_with_route import PermissionWithRoute
from ..serializers.permission_with_route_serializer import PermissionWithRouteSerializer
import redis

# API nay chi de goi private. API nay se luu tat ca lien ket giua cac API route cua cac service MyPT voi permission code xuong Redis
@api_view(["POST"])
def savePermissionWithRouteToRedis(request):
    qs = PermissionWithRoute.objects.all()
    serializer = PermissionWithRouteSerializer(qs, many=True)
    rows = serializer.data
    if len(rows) <= 0:
        return response_data(None, 6, "Khong co data")

    dataForRedis = {}
    for row in rows:
        serviceName = row.get("service_name")
        apiRoute = row.get("api_route")
        if dataForRedis.get(serviceName, None) is None:
            dataForRedis[serviceName] = {}
        perCodesStr = row.get("permission_codes").strip()
        perCodes = []
        if perCodesStr != "":
            perCodes = perCodesStr.split(",")
        dataForRedis[serviceName][apiRoute] = perCodes

    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                      , port=project_settings.REDIS_PORT_CENTRALIZED
                                      , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                      password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                      , decode_responses=True, charset="utf-8")
    resSaveRedis = redisInstance.set("permissionsWithRoutes", str(dataForRedis))
    print(resSaveRedis)

    return response_data({"resSaveRedis": resSaveRedis, "dataForRedis": dataForRedis})

# API nay chi de goi private. API nay se tra ve value cua key permissionsWithRoutes tu Redis
@api_view(["POST"])
def getPermissionWithRouteFromRedis(request):
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                      , port=project_settings.REDIS_PORT_CENTRALIZED
                                      , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                      password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                      , decode_responses=True, charset="utf-8")

    permissionsWithRoutesStr = redisInstance.get("permissionsWithRoutes")
    if permissionsWithRoutesStr is None:
        return response_data(None, 6, "Khong co redis permissionsWithRoutes")
    else:
        permissionsWithRoutesData = ast.literal_eval(permissionsWithRoutesStr)
        return response_data({"permissionsWithRoutesFromRedis": permissionsWithRoutesData})