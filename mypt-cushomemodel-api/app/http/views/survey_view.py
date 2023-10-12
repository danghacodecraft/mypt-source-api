from rest_framework.viewsets import ViewSet

from app.core.entities.app_user_token_validator import AppUserTokenValidator
from app.core.helpers.response import *
from app.http.serializers.house_model_survey_serializer import *
from ..models.house_model_survey_equipment import SurveyEquipments
from ..models.house_model_survey_net_package import SurveyNetPackage
from ..serializers.api_call_log_serializer import ApiCallLogSerializer
from ..serializers.house_model_survey_equipment_serializer import SurveyEquipmentSerializer
from ..serializers.house_model_survey_image_serializer import HouseModelSurveyImageSerializer
from ..serializers.house_model_survey_net_package_serializer import SurveyNetPackageSerializer
from ..validation.survey_validation import *
from core.helpers import global_variable as gb
from core.helpers.auth_session_handler import *
from core.helpers.utils import process_equipment_data


class CusHomeModelSurveyView(ViewSet):
    def post_create_custom_house_model_survey(self, request):
        try:
            with transaction.atomic():
                request_data = request.data.copy()
                header = request.headers.copy()
                app_id = header['App-Id']
                app_user_token = header['App-User-Token']
                data_token = getUserAuthSessionData(header.get("Authorization"))
                request_data['contractCode'] = request.contract_code
                request_data['regions'] = request_data.get('regions', 'Không có thông tin')
                request_data['branchFullName'] = request_data.get('branchFullName', 'Không có thông tin')
                request_data['statusSurvey'] = request_data.get('statusSurvey', 'Thiếu thông tin')

                if HouseModelSurvey.objects.filter(contract_code=request.contract_code).exists():
                    return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                         message=f'Đã tồn tại mô hình nhà với số hợp đồng {request.contract_code}')

                app_user_token_validator = AppUserTokenValidator()

                token_decrypt = app_user_token_validator.validateAppUserTokenAndAppId(app_user_token, app_id)
                data_token = {**data_token, **token_decrypt}
                request_data = {**data_token, **request_data}

                create_survey_serializer = ModelSurveyInfoValidate(data=request_data, many=False)
                if not create_survey_serializer.is_valid():
                    raise Exception(list(create_survey_serializer.errors.values())[0][0])
                else:
                    survey_serializer = create_survey_serializer.save()

                list_router = process_equipment_data(survey_serializer['routers'], survey_serializer['id'], 'modem')
                list_access_point = process_equipment_data(survey_serializer['accessPoints'], survey_serializer['id'],
                                                           'access_point')
                list_equipment = list_access_point + list_router

                list_net_package = [
                    {**i, 'idPackage': i.get('id', 0), 'modelSurveyId': survey_serializer['id'], 'modelType': 'model'}
                    for data in survey_serializer['internetPackages']
                    for i in survey_serializer['internetPackages'][data]
                ]
                net_package_serializer = SurveyNetPackageSerializer(data=list_net_package, many=True)
                if not net_package_serializer.is_valid():
                    raise Exception(net_package_serializer.errors)
                else:
                    net_package_serializer = net_package_serializer.save()

                equipment_serializer = SurveyEquipmentSerializer(data=list_equipment, many=True)
                if not equipment_serializer.is_valid():
                    raise Exception(equipment_serializer.errors)
                else:
                    equipment_serializer = equipment_serializer.save()
                list_data = [{'modelSurveyId': survey_serializer['id'],
                              'sdkUserId': data_token['userId'],
                              'appId': data_token['appId'],
                              'sdkAccUsername': data_token['accUsername'],
                              'floors': survey_serializer['floors'], **i} for i in request_data.get('listModel', [])]
                serializer_validate = HouseModelSurveyImageSerializer(data=list_data, many=True)
                if not serializer_validate.is_valid():
                    raise Exception(list(serializer_validate.errors[0].values())[0][0])
                else:
                    serializer_validate.save()

                try:
                    input_api_log = {
                        'apiUrl': request.get_full_path(),
                        'apiEnv': project_settings.APP_ENVIRONMENT,
                        'apiInput': str(request.data),
                        'apiOutput': None,
                        'deviceId': data_token['deviceId'],
                        'deviceName': data_token['deviceName'],
                        'deviceToken': data_token['deviceToken'],
                        'devicePlatform': data_token['devicePlatform'],
                        'sdkUserId': data_token['userId'],
                        'appId': data_token['appId'],
                        'sdkAccUsername': data_token['accUsername']
                    }
                    serializer = ApiCallLogSerializer(data=input_api_log)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        raise Exception(serializer.errors)
                except Exception as ex:
                    print(f'Error/Loi: {str(ex)}')

                # Thực hiện các hoạt động khác nếu cần

                # Nếu không có lỗi, commit các thay đổi vào database
                # Nếu có lỗi, thực hiện rollback tự động
        except Exception as ex:
            print('Error/Loi: ', str(ex))

            try:
                input_api_log = {
                    'apiUrl': request.get_full_path(),
                    'apiEnv': project_settings.APP_ENVIRONMENT,
                    'apiInput': str(request.data),
                    'apiOutput': None,
                    'deviceId': data_token['deviceId'],
                    'deviceName': data_token['deviceName'],
                    'deviceToken': data_token['deviceToken'],
                    'devicePlatform': data_token['devicePlatform'],
                    'sdkUserId': data_token['userId'],
                    'appId': data_token['appId'],
                    'sdkAccUsername': data_token['accUsername']
                }
                serializer = ApiCallLogSerializer(data=input_api_log)
                if serializer.is_valid():
                    serializer.save()
                else:
                    raise Exception(serializer.errors)
            except Exception as ex:
                print(f'Error/Loi: {str(ex)}')
            return response_data(status=gb.STATUS_CODE_FAILED, message=str(ex))
        return response_data(message='Khảo sát đã được lưu thành công')

    def post_update_custom_house_model_survey(self, request):
        try:
            with transaction.atomic():
                request_data = request.data.copy()
                header = request.headers
                app_id = header['App-Id']
                app_user_token = header['App-User-Token']
                data_token = getUserAuthSessionData(request.headers.get("Authorization"))
                request_data['contractCode'] = request.contract_code
                request_data['regions'] = request_data.get('regions', 'Không có thông tin')
                request_data['branchFullName'] = request_data.get('branchFullName', 'Không có thông tin')
                request_data['statusSurvey'] = request_data.get('statusSurvey', 'Thiếu thông tin')

                if not HouseModelSurvey.objects.filter(contract_code=request.contract_code).exists():
                    return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                         message=f'Không tồn tại mô hình nhà với số hợp đồng {request.contract_code} '
                                                 f'để thực hiện cập nhật')

                app_user_token_validator = AppUserTokenValidator()

                token_decrypt = app_user_token_validator.validateAppUserTokenAndAppId(app_user_token, app_id)
                data_token = {**data_token, **token_decrypt}
                request_data = {**data_token, **request_data}

                update_survey_serializer = UpdateModelSurveyValidate(data=request_data, many=False)
                if not update_survey_serializer.is_valid():
                    raise Exception(list(update_survey_serializer.errors.values())[0][0])
                else:
                    survey_serializer = update_survey_serializer.save()

                list_router = process_equipment_data(survey_serializer['routers'], survey_serializer['id'], 'modem')
                list_access_point = process_equipment_data(survey_serializer['accessPoints'], survey_serializer['id'],
                                                           'access_point')
                list_equipment = list_access_point + list_router

                list_net_package = [
                    {**i, 'idPackage': i.get('id', 0), 'modelSurveyId': survey_serializer['id'], 'modelType': 'model'}
                    for data in survey_serializer['internetPackages']
                    for i in survey_serializer['internetPackages'][data]
                ]
                net_package_serializer = SurveyNetPackageSerializer(data=list_net_package, many=True)
                if not net_package_serializer.is_valid():
                    raise Exception(net_package_serializer.errors)
                else:
                    net_package_serializer = net_package_serializer.save()

                equipment_serializer = SurveyEquipmentSerializer(data=list_equipment, many=True)
                if not equipment_serializer.is_valid():
                    raise Exception(equipment_serializer.errors)
                else:
                    equipment_serializer = equipment_serializer.save()

                try:
                    input_api_log = {
                        'apiUrl': request.get_full_path(),
                        'apiEnv': project_settings.APP_ENVIRONMENT,
                        'apiInput': str(request.data),
                        'apiOutput': None,
                        'deviceId': data_token['deviceId'],
                        'deviceName': data_token['deviceName'],
                        'deviceToken': data_token['deviceToken'],
                        'devicePlatform': data_token['devicePlatform'],
                        'sdkUserId': data_token['userId'],
                        'appId': data_token['appId'],
                        'sdkAccUsername': data_token['accUsername']
                    }
                    serializer = ApiCallLogSerializer(data=input_api_log)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        raise Exception(serializer.errors)
                except Exception as ex:
                    print(f'Error/Loi: {str(ex)}')
                # Thực hiện các hoạt động khác nếu cần

                # Nếu không có lỗi, commit các thay đổi vào database
                # Nếu có lỗi, thực hiện rollback tự động
        except Exception as ex:
            print('Error/Loi: ', str(ex))
            try:
                input_api_log = {
                    'apiUrl': request.get_full_path(),
                    'apiEnv': project_settings.APP_ENVIRONMENT,
                    'apiInput': str(request.data),
                    'apiOutput': None,
                    'deviceId': data_token['deviceId'],
                    'deviceName': data_token['deviceName'],
                    'deviceToken': data_token['deviceToken'],
                    'devicePlatform': data_token['devicePlatform'],
                    'sdkUserId': data_token['userId'],
                    'appId': data_token['appId'],
                    'sdkAccUsername': data_token['accUsername']
                }
                serializer = ApiCallLogSerializer(data=input_api_log)
                if serializer.is_valid():
                    serializer.save()
                else:
                    raise Exception(serializer.errors)
            except Exception as ex:
                print(f'Error/Loi: {str(ex)}')
            return response_data(status=gb.STATUS_CODE_FAILED, message='Lưu không thành công, vui lòng thử lại')
        return response_data(message='Khảo sát được cập nhật thành công')

    def get_history_model_survey(self, request):
        try:
            contract_code = request.contract_code
            house_model_list = HouseModelSurvey.objects.filter(contract_code=contract_code).order_by('-created_at')

            response = HouseModelSurveySerializer(house_model_list, many=True, fields=['id', 'sdkAccUsername',
                                                                                       'createdAt', 'isCurrent',
                                                                                       'reason'])
        except Exception as ex:
            print('Error/Loi: ', str(ex))
            return response_data(status=gb.STATUS_CODE_FAILED, message='Lấy dữ liệu không thành công')
        return response_data(data=response.data)

    def get_current_version_survey(self, request):
        try:
            contract_code = request.contract_code
            house_model = HouseModelSurvey.objects.filter(is_current=1, contract_code=contract_code)

            if not house_model.exists():
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT, message='Không tồn tại chi tiết mô hình nhà')

            # model_survey_id = house_model[0].id
            # queryset_net_survey = SurveyNetPackage.objects.filter(model_survey_id=model_survey_id)
            # serializer_net_survey = SurveyNetPackageSerializer(queryset_net_survey, many=True)
            #
            # queryset_equipment_survey = SurveyEquipments.objects.filter(model_survey_id=model_survey_id)
            # serializer_equipment_survey = SurveyEquipmentSerializer(queryset_equipment_survey, many=True)
            #
            # serializer_modem = [data for data in serializer_equipment_survey.data if
            #                     data['modemRule'] == 'Modem']
            #
            # serializer_access_point = [data for data in serializer_equipment_survey.data if
            #                            data['modemRule'] == 'Access Point']
            #
            # net_package = {
            #     'internetPackages': {
            #         'result': [],
            #         'present': []
            #     }
            # }
            # for data in serializer_net_survey.data:
            #     id_package = int(data['idPackage'])
            #     data_copy = {
            #         'id': id_package,
            #         'name': data['name'],
            #         'downloadSpeed': data['downloadSpeed'],
            #         'uploadSpeed': data['uploadSpeed'],
            #         'quantity': data['quantity'],
            #     }
            #     if id_package == 0:
            #         net_package['internetPackages']['present'].append(data_copy)
            #     else:
            #         net_package['internetPackages']['result'].append(data_copy)
            #
            # modem_equipment = {
            #     'routers': {
            #         'result': [],
            #         'present': [],
            #     }
            # }
            # for item in serializer_modem:
            #     id_equipment = int(item['idEquipment'])
            #     data_copy = {
            #         'id': id_equipment,
            #         'name': item['name'],
            #         'LANWifi': item['LANWifi'],
            #         'wifi': item['wifi'],
            #         'wifi24Pow': item['wifi24Pow'],
            #         'wifi5Pow': item['wifi5Pow'],
            #         'quantity': item['quantity']
            #     }
            #     if id_equipment == 0:
            #         modem_equipment['routers']['present'].append(data_copy)
            #     else:
            #         modem_equipment['routers']['result'].append(data_copy)
            #
            # access_point_equipment = {
            #     'accessPoints': {
            #         'result': {
            #             'model': [],
            #             'other': []
            #         },
            #         'present': []
            #     }
            # }
            # for item in serializer_access_point:
            #     id_equipment = int(item['idEquipment'])
            #     data_copy = {
            #         'id': id_equipment,
            #         'name': item['name'],
            #         'LANWifi': item['LANWifi'],
            #         'wifi': item['wifi'],
            #         'wifi24Pow': item['wifi24Pow'],
            #         'wifi5Pow': item['wifi5Pow'],
            #         'quantity': item['quantity']
            #     }
            #     if id_equipment == 0:
            #         access_point_equipment['accessPoints']['present'].append(data_copy)
            #     else:
            #         if item['modelType'] == 'model':
            #             access_point_equipment['accessPoints']['result']['model'].append(data_copy)
            #         else:
            #             access_point_equipment['accessPoints']['result']['other'].append(data_copy)
            #
            # resp = \
            #     HouseModelSurveySerializer(house_model, many=True, fields=[
            #         'contractCode', 'regions', 'branchFullName', 'sdkAccUsername', 'idType', 'modelType',
            #         'customerType', 'houseLength', 'houseWidth', 'floors', 'rowsPerFloor', 'roomsPerRow',
            #         'peoplePerRoom', 'userWifi', 'userLAN', 'userCamera', 'luxPackageCheck', 'uploadAlotCheck',
            #         'concurrentUsageRate', 'otherCheck', 'otherWidth', 'otherLength', 'otherLength', 'otherUserWifi',
            #         'totalAP', 'conclusion', 'reason', 'createdAt']).data[0]
            # resp = {**resp, **access_point_equipment, **modem_equipment, **net_package}

            resp = \
                HouseModelSurveySerializer(house_model, many=True, fields=[
                    'contractCode', 'regions', 'branchFullName', 'sdkAccUsername', 'idType', 'modelType',
                    'customerType', 'houseLength', 'houseWidth', 'floors', 'rowsPerFloor', 'roomsPerRow',
                    'peoplePerRoom', 'userWifi', 'userLAN', 'userCamera', 'luxPackageCheck', 'uploadAlotCheck',
                    'concurrentUsageRate', 'otherCheck', 'otherWidth', 'otherLength', 'otherLength', 'otherUserWifi',
                    'internetPackages', 'routers', 'accessPoints', 'totalAP', 'conclusion',
                    'reason', 'createdAt']).data[0]

        except Exception as ex:
            print('Error/Loi: ', str(ex))
            return response_data(status=gb.STATUS_CODE_FAILED, message='Lấy thông tin chi tiết mô hình nhà thất bại')
        return response_data(data=resp)

    def get_detail_model_survey(self, request):
        try:
            model_survey_id = request.data.get('id', None)

            if not model_survey_id:
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                     message='Không tồn tại id chi tiết mô hình nhà')

            house_model = HouseModelSurvey.objects.get(id=model_survey_id)

            # model_survey_id = house_model[0].id
            # queryset_net_survey = SurveyNetPackage.objects.filter(model_survey_id=model_survey_id)
            # serializer_net_survey = SurveyNetPackageSerializer(queryset_net_survey, many=True)
            #
            # queryset_equipment_survey = SurveyEquipments.objects.filter(model_survey_id=model_survey_id)
            # serializer_equipment_survey = SurveyEquipmentSerializer(queryset_equipment_survey, many=True)
            #
            # serializer_modem = [data for data in serializer_equipment_survey.data if
            #                     data['modemRule'] == 'Modem']
            #
            # serializer_access_point = [data for data in serializer_equipment_survey.data if
            #                            data['modemRule'] == 'Access Point']
            #
            # net_package = {
            #     'internetPackages': {
            #         'result': [],
            #         'present': []
            #     }
            # }
            # for data in serializer_net_survey.data:
            #     id_package = int(data['idPackage'])
            #     data_copy = {
            #         'id': id_package,
            #         'name': data['name'],
            #         'downloadSpeed': data['downloadSpeed'],
            #         'uploadSpeed': data['uploadSpeed'],
            #         'quantity': data['quantity'],
            #     }
            #     if id_package == 0:
            #         net_package['internetPackages']['present'].append(data_copy)
            #     else:
            #         net_package['internetPackages']['result'].append(data_copy)
            #
            # modem_equipment = {
            #     'routers': {
            #         'result': [],
            #         'present': [],
            #     }
            # }
            # for item in serializer_modem:
            #     id_equipment = int(item['idEquipment'])
            #     data_copy = {
            #         'id': id_equipment,
            #         'name': item['name'],
            #         'LANWifi': item['LANWifi'],
            #         'wifi': item['wifi'],
            #         'wifi24Pow': item['wifi24Pow'],
            #         'wifi5Pow': item['wifi5Pow'],
            #         'quantity': item['quantity']
            #     }
            #     if id_equipment == 0:
            #         modem_equipment['routers']['present'].append(data_copy)
            #     else:
            #         modem_equipment['routers']['result'].append(data_copy)
            #
            # access_point_equipment = {
            #     'accessPoints': {
            #         'result': {
            #             'model': [],
            #             'other': []
            #         },
            #         'present': []
            #     }
            # }
            # for item in serializer_access_point:
            #     id_equipment = int(item['idEquipment'])
            #     data_copy = {
            #         'id': id_equipment,
            #         'name': item['name'],
            #         'LANWifi': item['LANWifi'],
            #         'wifi': item['wifi'],
            #         'wifi24Pow': item['wifi24Pow'],
            #         'wifi5Pow': item['wifi5Pow'],
            #         'quantity': item['quantity']
            #     }
            #     if id_equipment == 0:
            #         access_point_equipment['accessPoints']['present'].append(data_copy)
            #     else:
            #         if item['modelType'] == 'model':
            #             access_point_equipment['accessPoints']['result']['model'].append(data_copy)
            #         else:
            #             access_point_equipment['accessPoints']['result']['other'].append(data_copy)
            #
            # resp = \
            #     HouseModelSurveySerializer(house_model, many=True, fields=[
            #         'contractCode', 'regions', 'branchFullName', 'sdkAccUsername', 'idType', 'modelType',
            #         'customerType', 'houseLength', 'houseWidth', 'floors', 'rowsPerFloor', 'roomsPerRow',
            #         'peoplePerRoom', 'userWifi', 'userLAN', 'userCamera', 'luxPackageCheck', 'uploadAlotCheck',
            #         'concurrentUsageRate', 'otherCheck', 'otherWidth', 'otherLength', 'otherLength', 'otherUserWifi',
            #         'totalAP', 'conclusion', 'reason', 'createdAt']).data[0]
            # resp = {**resp, **access_point_equipment, **modem_equipment, **net_package}

            resp = HouseModelSurveySerializer(house_model, many=False, fields=[
                    'contractCode', 'regions', 'branchFullName', 'sdkAccUsername', 'idType', 'modelType',
                    'customerType', 'houseLength', 'houseWidth', 'floors', 'rowsPerFloor', 'roomsPerRow',
                    'peoplePerRoom', 'userWifi', 'userLAN', 'userCamera', 'luxPackageCheck', 'uploadAlotCheck',
                    'concurrentUsageRate', 'otherCheck', 'otherWidth', 'otherLength', 'otherLength', 'otherUserWifi',
                    'internetPackages', 'routers', 'accessPoints', 'totalAP', 'conclusion',
                    'reason', 'createdAt']).data
        except Exception as ex:
            print('Error/Loi: ', str(ex))
            if str(ex) == 'HouseModelSurvey matching query does not exist.':
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT, message='Không tồn tại chi tiết mô hình nhà')
            return response_data(status=gb.STATUS_CODE_FAILED, message='Lấy thông tin chi tiết mô hình nhà thất bại')
        return response_data(data=resp)
