from rest_framework.viewsets import ModelViewSet

from ..models.current_contract_info_log import CurrentContractInfoLog
from ..serializers.config_serializer import ConfigsSerializer
from ..serializers.current_contract_info_log_serializer import CurrentContractInfoLogSerializer
from ...core.helpers.response import *


class CurrentContractInfoLogView(ModelViewSet):

    def list(self, request, *args, **kwargs):
        # Đầu tiên, gọi phương thức gốc của lớp cha để lấy dữ liệu
        queryset = CurrentContractInfoLog.objects.all()
        serializer = CurrentContractInfoLogSerializer(queryset, many=True)
        result = serializer.data
        return response_data(result)

    def retrieve(self, request, *args, **kwargs):
        pass

    def create(self, request, *args, **kwargs):
        pass
