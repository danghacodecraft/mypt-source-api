from django.db import transaction
from rest_framework.viewsets import ViewSet

from ..models.proposed_equipment import ProposedEquipment
from ..serializers.proposed_equipment_serializer import ProposedEquipmentSerializer
from ...core.entities.app_user_token_validator import AppUserTokenValidator
from ...core.helpers import global_variable as gb
from ...core.helpers.auth_session_handler import getUserAuthSessionData
from ...core.helpers.response import *
from ...core.helpers.utils import return_choice_name


class ProposedEquipmentView(ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            queryset = ProposedEquipment.objects.all()
            serializer = ProposedEquipmentSerializer(queryset, many=True)
            result = serializer.data
        except Exception as ex:
            print('Error/Loi: {}'.format(str(ex)))
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_SYSTEM)
        return response_data(result)

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request_data = request.data.copy()
                header = request.headers
                app_id = header['App-Id']
                app_user_token = header['App-User-Token']
                data_token = getUserAuthSessionData(request.headers.get("Authorization"))

                app_user_token_validator = AppUserTokenValidator()

                token_decrypt = app_user_token_validator.validateAppUserTokenAndAppId(app_user_token, app_id)
                data_token = {**data_token, **token_decrypt}
                data_token['sdkUserId'] = data_token['userId']
                data_token['sdkAccUsername'] = data_token['accUsername']
                request_data = {**data_token, **request_data, 'sdkUserId': data_token['userId'],
                                'sdkAccUsername': data_token['accUsername'],
                                'deviceOrigin': return_choice_name(data_token['appId'],
                                                                   ProposedEquipment.DEVICE_ORIGIN_CHOICES)}

                serializer = ProposedEquipmentSerializer(data=request_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    raise Exception(list(serializer.errors.values())[0][0])
        except Exception as ex:
            print('Error/Loi: {}'.format(str(ex)))
            return response_data(status=gb.STATUS_CODE_FAILED, message=str(ex))
        return response_data(message='Thêm thiết bị đề xuất thành công')
