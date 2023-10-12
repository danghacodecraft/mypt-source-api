import json

from rest_framework.viewsets import ModelViewSet

from ..models.configs import Configs
from ..serializers.config_serializer import ConfigsSerializer
from core.helpers.my_datetime import getFormatDatetimeNow
from core.helpers.response import *


class ConfigView(ModelViewSet):
    queryset = Configs.objects.all()
    serializer_class = ConfigsSerializer

    def list(self, request, *args, **kwargs):
        result = None
        # Đầu tiên, gọi phương thức gốc của lớp cha để lấy dữ liệu
        queryset = Configs.objects.all()
        serializer = ConfigsSerializer(queryset, many=True)
        result = serializer.data
        return response_data(result)

    def retrieve(self, request, *args, **kwargs):

        return response_data()

    def create(self, request, *args, **kwargs):
        try:
            request_data = request.data
            config_key = request_data['configKey'].upper()
            config_value = request_data['configValue']
            if isinstance(config_value, dict):
                config_value = json.dumps(config_value)
            data = Configs.objects.create(config_type=Configs.CONSTANT, config_key=config_key,
                                          config_description_vi=request_data['configDescVI'],
                                          config_description_en=request_data['configDescEN'],
                                          config_value=config_value,
                                          created_at=getFormatDatetimeNow(),
                                          note=request_data['note'])
            data.save()
            serializer = ConfigsSerializer(data)
        except Exception as ex:
            print(str(ex))
            return response_data(message=str(ex), status=0)
        return response_data(serializer.data)
