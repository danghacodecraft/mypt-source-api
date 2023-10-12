from ..serializers.emp_checkin_serializer import *
from ..serializers.account_management_serializer import *
from ..serializers.emp_checkin_history_serializer import *
from ..paginations.custom_pagination import *
from ...core.helpers.response import *
from django.conf import settings as project_settings

import redis
from rest_framework import status
from rest_framework.viewsets import ViewSet


class HealthCheckView(ViewSet):
    def health_check(self, request):
        # test lay domain name tu request
        domainName = request.get_host()

        # test ket noi mysql db
        try:
            queryset = EmpCheckin.objects.filter(checkin_day="2021-12-12")
            count = EmpCheckin.objects.count()
            paginator = StandardPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = EmpCheckinSerializer(result, many=True)
            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                'newsList': serializer.data
            }
            print('data ok')
            print(data)
        except:
            print('data not ok')
            return Response({'status': 0, 'message': 'data connection not ok'}, status.HTTP_200_OK)

        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("profile", "Day la value cua Redis key profile abcdef 123969", 3600)
        print("redis value : " + redisInstance.get("profile"))

        print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
        print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
        print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

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