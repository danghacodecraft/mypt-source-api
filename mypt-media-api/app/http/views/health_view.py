from core.helpers.response import *
from ..serializers.storage_uuid_serializer import *
from ..paginations.custom_pagination import *
import redis
from django.conf import settings as project_settings
from app.configs import app_settings
from rest_framework.viewsets import ViewSet
from rest_framework import status


class HealthView(ViewSet):
    def health(self, request):
        domainName = request.get_host()
        try:
            queryset = StorageUuid.objects.all()
            count = queryset.count()
            paginator = StandardPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = StorageUuidSerializer(result, many=True)
            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                'newsList': serializer.data
            }
            print('data ok')
            print(data)
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

        resData = {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "testRedisVal": redisInstance.get("profile"),
            "domainName": domainName
        }

        return response_data(data=resData, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

    def add_kong(self, request):
        return response_data(data='ok')
