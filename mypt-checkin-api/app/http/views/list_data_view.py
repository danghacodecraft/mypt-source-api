from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


from ..serializers.response_content_serializer import *
from ...core.helpers.response import *
from rest_framework.decorators import api_view

from ...http.entities import global_data
from ...core.helpers import auth_session_handler as authSessionHandler

class ListDataView(ViewSet):
    def list_response(self, request):
        status_api = 1
        msg = "Xem thông tin thành công"
        data = []
        try:
            queryset = ResponseContent.objects.exclude(content="")
            serializer = ResponseContentSerializer(queryset, many=True)
            data_query = serializer.data
            if len(data_query) > 0:
                for i in data_query:
                    dict_tmp = {
                        "id": i['idContent'],
                        "content": i['contentResponse']
                    }
                    data.append(dict_tmp)

        except Exception as e:
            print("------------------list_response---------------")
            print(e)

        return response_data(data=data, status=status_api, message=msg)