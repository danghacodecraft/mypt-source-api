import redis
from django.conf import settings as project_settings
from rest_framework import status
from rest_framework.viewsets import ViewSet

from ..models.configs import Configs
from ..paginations.custom_pagination import *
from ..serializers.config_serializer import ConfigsSerializer
from core.helpers.response import *


class HealthView(ViewSet):
    def health(self, request):
        domainName = request.get_host()
        try:
            queryset = Configs.objects.all()
            count = queryset.count()
            paginator = StandardPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = ConfigsSerializer(result, many=True)
            data = {
                    'numberPage': count//StandardPagination.page_size+1,
                    'newsList': serializer.data
                }
            print('data ok')
        except Exception as ex:
            print(ex)
            print('data not ok')
            return Response({'statusCode': 0, 'message': 'data connection not ok'}, status.HTTP_200_OK)

        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("test_connect", "Day la value cua Redis key test_connect abcdef 123969", 3600)
        print("redis value : " + redisInstance.get("test_connect"))

        print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
        print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
        print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

        resData = {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "testRedisVal": redisInstance.get("test_connect"),
            "domainName": domainName
        }

        return response_data(data=resData)

    def add_kong(self, request):
        return response_data(data='ok')
