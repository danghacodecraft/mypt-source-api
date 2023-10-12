from django.conf import settings as project_settings
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ViewSet

from app.core.entities.app_user_token_validator import AppUserTokenValidator
from app.core.helpers import global_variable as gb
from app.core.helpers.auth_session_handler import getUserAuthSessionData
from app.core.helpers.my_datetime import getFormatDatetimeNow
from app.core.helpers.response import response_data
from app.http.models.house_model_survey import HouseModelSurvey
from app.http.models.house_model_survey_equipment import SurveyEquipments
from app.http.models.house_model_survey_image import HouseModelSurveyImage
from app.http.models.house_model_survey_net_package import SurveyNetPackage
from app.http.serializers.api_call_log_serializer import ApiCallLogSerializer
from app.http.serializers.house_model_survey_image_serializer import HouseModelSurveyImageSerializer, \
    UpdateHouseModelSurveyImageSerializer
from app.http.validation.build_house_model_validation import UpdateHouseModelValidate


class BuildCusHomeModelView(ViewSet):
    def post_create_house_model(self, request):
        try:
            with transaction.atomic():
                contract_code = request.contract_code
                request_data = request.data.copy()
                request_data['contractCode'] = contract_code
                data_token = getUserAuthSessionData(request.headers.get("Authorization"))

                queryset = HouseModelSurvey.objects.filter(contract_code=contract_code, is_current=1) \
                    .order_by('-created_at')
                if len(queryset) <= 0:
                    return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                         message=f'Không tồn tại khảo sát cho mô hình nhà với số hợp đồng '
                                                 f'{contract_code}')
                model_survey_id = queryset[0].id
                if HouseModelSurveyImage.objects.filter(model_survey_id=model_survey_id).exists():
                    return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                         message=f'Đã dựng mô hình nhà cho số hợp đồng {contract_code}')
                list_data = request_data.get('listData', [])
                if not list_data:
                    raise Exception('Không có thông tin mô hình nhà')
                list_data = [{'modelSurveyId': model_survey_id,
                              'sdkUserId': data_token['userId'],
                              'appId': data_token['appId'],
                              'sdkAccUsername': data_token['accUsername'], **i} for i in list_data]
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
        return response_data(status=1, message='Lưu mô hình nhà thành công')

    def post_update_house_model(self, request):
        try:
            with transaction.atomic():
                contract_code = request.contract_code
                request_data = request.data.copy()
                request_data['contractCode'] = contract_code
                txt_status_updated = 'statusUpdated này là cập nhật là mô hình hiện có'

                header = request.headers
                app_id = header['App-Id']
                app_user_token = header['App-User-Token']
                data_token = getUserAuthSessionData(request.headers.get("Authorization"))

                app_user_token_validator = AppUserTokenValidator()

                token_decrypt = app_user_token_validator.validateAppUserTokenAndAppId(app_user_token, app_id)
                data_token = {**data_token, **token_decrypt}

                queryset_survey = HouseModelSurvey.objects.filter(contract_code=contract_code, is_current=1) \
                    .order_by('-created_at')
                if len(queryset_survey) <= 0:
                    return response_data(status=0,
                                         message=f"Không tồn tại khảo sát cho mô hình nhà với số hợp đồng {contract_code}")
                existing_survey = queryset_survey[0]
                existing_model_images = HouseModelSurveyImage.objects.filter(model_survey_id=existing_survey.id)
                # if not existing_model_images[0]: return response_data(status=0, message=f"Chưa từng lưu mô hình nhà
                # cho số hợp đồng {contract_code} " f"đã lưu trước đây")
                if existing_model_images:
                    status_updated = existing_model_images[0].status_updated
                    if status_updated == 0:
                        request_data['reason'] = txt_status_updated

                serializer_validate = UpdateHouseModelValidate(data=request_data)
                if not serializer_validate.is_valid():
                    return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                         message=list(serializer_validate.errors.values())[0][0])
                data = serializer_validate.validated_data
                list_data = data['listModel']

                if request_data['reason'] != txt_status_updated:
                    try:
                        # set lại tất cả khảo biến is_current bằng 0
                        queryset_survey.update(is_current=0)
                        # cập nhật sẽ tạo ra một dòng mới thay với is_curret = 1 và có reason
                        new_object_survey = HouseModelSurvey()
                        new_object_survey.__dict__.update(existing_survey.__dict__)
                        new_object_survey.id = None
                        new_object_survey.is_current = 1
                        new_object_survey.sdk_user_id = data_token['userId']
                        new_object_survey.app_id = data_token['appId']
                        new_object_survey.sdk_acc_username = data_token['accUsername']
                        new_object_survey.reason = data['reason']
                        new_object_survey.created_at = getFormatDatetimeNow()
                        new_object_survey.save()
                        model_survey_id = new_object_survey.id
                        total_floors = new_object_survey.floors

                        existing_survey_net_package = SurveyNetPackage.objects.filter(
                            model_survey_id=existing_survey.id)
                        existing_survey_equipment = SurveyEquipments.objects.filter(model_survey_id=existing_survey.id)
                        new_net_package_objects = []
                        new_equipment_objects = []
                        for obj in existing_survey_net_package:
                            new_obj = SurveyNetPackage(
                                model_survey_id=model_survey_id,
                                id_package=obj.id_package,
                                name=obj.name,
                                download_speed=obj.download_speed,
                                upload_speed=obj.upload_speed,
                                quantity=obj.quantity,
                                model_type=obj.model_type
                            )
                            new_net_package_objects.append(new_obj)
                        SurveyNetPackage.objects.bulk_create(new_net_package_objects)

                        for obj in existing_survey_equipment:
                            new_obj = SurveyEquipments(
                                model_survey_id=model_survey_id,
                                id_equipment=obj.id_equipment,
                                parent_name=obj.parent_name,
                                modem_rule=obj.modem_rule,
                                lan_wifi=obj.lan_wifi,
                                wifi=obj.wifi,
                                wifi_24_ghz=obj.wifi_24_ghz,
                                wifi_5_ghz=obj.wifi_5_ghz,
                                quantity=obj.quantity,
                                model_type=obj.model_type
                            )
                            new_equipment_objects.append(new_obj)
                        SurveyEquipments.objects.bulk_create(new_equipment_objects)
                    except Exception as ex:
                        raise Exception('Lỗi cập nhật: ' + str(ex))

                    list_data = [{'modelSurveyId': model_survey_id,
                                  'sdkUserId': data_token['userId'],
                                  'appId': data_token['appId'],
                                  'sdkAccUsername': data_token['accUsername'],
                                  'floors': total_floors, **i} for i in list_data]

                    serializer = HouseModelSurveyImageSerializer(data=list_data, many=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        errors = serializer.errors
                        raise Exception(errors)
                else:
                    list_data = [{'modelSurveyId': existing_survey.id,
                                  'sdkUserId': data_token['userId'],
                                  'appId': data_token['appId'],
                                  'sdkAccUsername': data_token['accUsername'],
                                  'floors': existing_survey.floors, **i} for i in list_data]
                    serializer = UpdateHouseModelSurveyImageSerializer(data=list_data, many=True)
                    if serializer.is_valid():
                        serializer.save()
                        HouseModelSurveyImage.objects.filter(model_survey_id=existing_survey.id)\
                            .update(status_updated=1,
                                    sdk_user_id=data_token['userId'],
                                    app_id=data_token['appId'],
                                    sdk_acc_username=data_token['accUsername'])
                    else:
                        errors = serializer.errors
                        raise Exception(str(errors))

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
                    print('ErrorLog/LoiLog: ', str(ex))
        except ValidationError as ex:
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
                print('ErrorLog/LoiLog: ', str(ex))
            return response_data(status=gb.STATUS_CODE_FAILED, message=str(ex.detail[0]))
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
                print('ErrorLog/LoiLog: ', str(ex))
            return response_data(status=gb.STATUS_CODE_FAILED,
                                 message='Cập nhật mô hình nhà không thành công: ' + str(ex))
        return response_data(status=1, message="Cập nhật mô hình nhà thành công")

    def get_current_house_model(self, request):
        try:
            contract_code = request.contract_code
            try:
                model_survey_id = HouseModelSurvey.objects.get(contract_code=contract_code, is_current=1).id
            except Exception as ex:
                print(f'Error/Loi: {str(ex)}')
                return response_data(status=0, message="Chưa dựng mô hình nhà")
            queryset = HouseModelSurveyImage.objects.filter(model_survey_id=model_survey_id).order_by('house_floor')
            if not queryset:
                return response_data(status=gb.STATUS_CODE_NO_DATA, message=gb.MESSAGE_API_NO_DATA)
            serializer = HouseModelSurveyImageSerializer(queryset, many=True, fields=['floor', 'size', 'devices',
                                                                                      'sketches', 'sketchesType'])
            result = {
                'sdkAccUsername': queryset[0].sdk_acc_username,
                'createdAt': queryset[0].created_at,
                'listModel': list(serializer.data)
            }

        except Exception as ex:
            print(f'Error/Loi: {str(ex)}')
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_SYSTEM)
        return response_data(result)

    def get_detail_house_model(self, request):
        try:
            request_data = request.data
            if request_data['modelSurveyId'] == '' or request_data['modelSurveyId'] == 0:
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT, message=gb.MESSAGE_API_NO_INPUT)

            model_survey_id = request_data['modelSurveyId']

            queryset = HouseModelSurveyImage.objects.filter(model_survey_id=model_survey_id).order_by('house_floor')
            if not queryset:
                return response_data(status=gb.STATUS_CODE_NO_DATA, message=gb.MESSAGE_API_NO_DATA)
            serializer = HouseModelSurveyImageSerializer(queryset, many=True, fields=['floor', 'size', 'devices',
                                                                                      'sketches', 'sketchesType'])
            result = {
                'sdkAccUsername': queryset[0].sdk_acc_username,
                'createdAt': queryset[0].created_at,
                'listModel': list(serializer.data)
            }
        except Exception as ex:
            print(f'Error/Loi: {str(ex)}')
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_SYSTEM)
        return response_data(data=result)
