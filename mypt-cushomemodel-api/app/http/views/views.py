import base64
import json

import requests
from django.http import HttpResponse
from rest_framework.viewsets import ViewSet

from app.configs import app_settings
from app.core.helpers import utils as utHelper
from ..models.configs import Configs
from ..models.house_model_type import HouseModelType
from ..models.material_loss import MaterialLoss
from ..models.template_groups import TemplateGroups
from ..models.templates import Templates
from ..serializers.api_call_log_serializer import ApiCallLogSerializer
from ..serializers.config_serializer import ConfigsSerializer
from ..serializers.current_contract_info_log_serializer import CurrentContractInfoLogSerializer
from ..serializers.house_model_type_serializer import HouseModelTypeSerializer
from ..serializers.material_loss_serializer import MaterialLossSerializer
from ..serializers.template_groups_serializer import TemplateGroupsSerializer
from ..serializers.templates_serializer import TemplatesSerializer
from ..validation.views_validation import InputCalculateModelValidate, TransformImageValidate
from ...configs.service_api_config import INSIDE_CONFIG, AI_MODEL_2D, SERVICE_CONFIG
from ...core.entities.app_user_token_validator import AppUserTokenValidator
from ...core.entities.calculation_formula_model import calculation_model
from ...core.helpers import global_variable as gb, utils
from ...core.helpers.auth_session_handler import *
from ...core.helpers.my_datetime import get_second_now_to_end_day
from ...core.helpers.response import *


class CusHomeModelView(ViewSet):
    def calculate_model_equipment(self, request, *args, **kwargs):
        try:
            result = None
            request_data = request.data.copy()
            data_token = getUserAuthSessionData(request.headers.get("Authorization"))
            redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                               port=project_settings.REDIS_PORT_CENTRALIZED,
                                               db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                               decode_responses=True, charset="utf-8")
            redis_instance.set(f'currentEquipmentInfo:{request.contract_code}', json.dumps({
                'regions': request_data['regions'],
                'branchFullName': request_data['branchFullName'],
                'internetPackages': request_data['internetPackages'],
                'routers': request_data['routers'],
                'accessPoints': request_data['accessPoints'],
                'totalAP': request_data['totalAP']
            }), int(get_second_now_to_end_day()))

            serializer_validate = InputCalculateModelValidate(data=request_data)
            if not serializer_validate.is_valid():
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                     message=list(serializer_validate.errors.values())[0][0])
            calculate = calculation_model(data=serializer_validate.validated_data)
            if calculate is None:
                return response_data(status=gb.STATUS_CODE_ERROR_LOGIC, message='Tính toán thông số lỗi')
            result = serializer_validate.validated_data
            result.pop('contractCode')
            result['userWifi'] = calculate['userWifi']
            result['totalAP'] = {
                'result': calculate['totalAP'],
                'present': result['totalAP']
            }
            result['accessPoints'] = {
                'result': calculate['accessPoints'],
                'present': request_data['accessPoints']
            }
            result['internetPackages'] = {
                'result': calculate['internetPackages'],
                'present': request_data['internetPackages']
            }
            result['routers'] = {
                'result': calculate['routers'],
                'present': request_data['routers']
            }
            result['conclusion'] = calculate['conclusion']
            result['statusSurvey'] = calculate['statusSurvey']

            try:
                input_api_log = {
                    'apiUrl': request.get_full_path(),
                    'apiEnv': project_settings.APP_ENVIRONMENT,
                    'apiInput': str(request.data),
                    'apiOutput': str(result),
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
            print(f'Error/Loi: {str(ex)}')
            # data_token = getUserAuthSessionData(request.headers.get("Authorization"))
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
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_SYSTEM)
        return response_data(result)

    def get_types_model(self, request, *args, **kwargs):
        try:
            serializer_house_model = HouseModelTypeSerializer(HouseModelType.objects.filter(model_type=1, is_active=1)
                                                              .order_by('id'), many=True, fields=['id', 'name'])
            serializer_material_loss = MaterialLossSerializer(MaterialLoss.objects.all().order_by('id'),
                                                              many=True, fields=['id', 'name', 'loss', 'colorCode'])
            serializer_thickness_parameter = \
                ConfigsSerializer(Configs.objects.get(config_key='OBSTACLE_THICKNESS_PARAMETERS'),
                                  many=False).data['configValue']
            result = {
                'modelType': serializer_house_model.data,
                'customerType': [
                    {
                        'id': 1,
                        'name': 'Cá nhân'
                    },
                    {
                        'id': 2,
                        'name': 'Doanh nghiệp'
                    }
                ],
                'materialLoss': serializer_material_loss.data,
                'thicknessParameters': serializer_thickness_parameter
            }
        except Exception as ex:
            print(f'Error/Loi: {str(ex)}')
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_SYSTEM)
        return response_data(result)

    def get_template_model(self, request, *args, **kwargs):
        try:
            result = []
            request_data = request.data.copy()
            id_model_type_encrypt = request.GET.get('id').replace(' ', '+')
            id_model_type = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, id_model_type_encrypt)

            order_group_template = json.loads(
                HouseModelType.objects.get(id=id_model_type, model_type=HouseModelType.MAIN).group_template)
            new_order_group_template = []

            template_queryset = Templates.objects.all().order_by('id')
            serializer_template = TemplatesSerializer(template_queryset, many=True, fields=['id', 'groupID', 'sketches',
                                                                                            'imageURL'])

            group_queryset = TemplateGroups.objects.all().order_by('id')
            group_serializer = TemplateGroupsSerializer(group_queryset, many=True, fields=['id', 'name']).data

            # sắp xếp thứ tự ưu tiên của group
            for idx in range(len(order_group_template)):
                for item in group_serializer:
                    if item['id'] == order_group_template[idx]:
                        new_order_group_template.append(item)
                        group_serializer.remove(item)

            # phân chia template cho từng group
            for template in serializer_template.data:
                for group in new_order_group_template:
                    if 'templates' not in group:
                        group['templates'] = []
                    if template['groupID'] == group['id']:
                        template['name'] = 'Mẫu ' + str(len(group['templates']) + 1)
                        group['templates'].append(template)
                template.pop('groupID')
            result = new_order_group_template
        except Exception as ex:
            print(f'Error/Loi: {str(ex)}')
            if 'HouseModelType matching query does not exist' in str(ex):
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT, message='Mã nhóm mẫu không hợp lệ')
            if 'Incorrect padding' in str(ex):
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT, message='ID không hợp lệ')
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_SYSTEM)
        return response_data(result)

    def transform_image(self, request, *args, **kwargs):
        try:
            data_token = getUserAuthSessionData(request.headers.get("Authorization"))
            request_data = request.data.copy()
            serializer = TransformImageValidate(data=request_data)
            if not serializer.is_valid():
                return response_data(status=gb.STATUS_CODE_INVALID_INPUT,
                                     message=list(serializer.errors.values())[0][0])
            input_data = serializer.validated_data
            base_env = project_settings.APP_ENVIRONMENT
            url = AI_MODEL_2D['MODEL_2D'][base_env]['url'] + AI_MODEL_2D['MODEL_2D']['transform_image_app']['func']
            data = {
                'file': input_data['image']
            }
            payload = {
                'sketches': input_data['sketches'],
                'type': input_data['sketchesType']
            }
            if base_env == 'local':
                proxies = {}
            else:
                proxies = {
                    "http": "http://proxy.hcm.fpt.vn:80",
                    "https": "http://proxy.hcm.fpt.vn:80"
                }
            response = requests.post(url, data=payload, files=data, proxies=proxies)

            if response.status_code == 200:
                response = json.loads(response.text)
                # response['houseFloor'] = int(request.data.get('houseFloor', 0))
            elif response.status_code == 504:
                return response_data(None, status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_TIMEOUT)
            else:
                print(response.content)
                print(response.status_code)
                raise Exception

            # lưu log bên thứ 3 - AI
            input_api_log = {
                'apiUrl': url,
                'apiEnv': AI_MODEL_2D['MODEL_2D'][base_env]['env'],
                'apiInput': str(request.data),
                'apiOutput': str(response),
                'deviceId': data_token['deviceId'],
                'deviceName': data_token['deviceName'],
                'deviceToken': data_token['deviceToken'],
                'devicePlatform': data_token['devicePlatform'],
                'sdkUserId': data_token['userId'],
                'appId': data_token['appId'],
                'sdkAccUsername': data_token['accUsername']
            }

        except Exception as ex:
            print('Error/Loi: ', ex)
            return response_data(None, status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_LOGIC)
        return response_data(response)

    def current_equipments_info_list(self, request, *args, **kwargs):
        try:
            redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                               port=project_settings.REDIS_PORT_CENTRALIZED,
                                               db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                               decode_responses=True, charset="utf-8")

            result = {
                'regions': '',
                'branchFullName': '',
                'internetPackages': [],
                'routers': [],
                'accessPoints': [],
                'totalAP': 0
            }
            contract_code = request.contract_code
            redis_contract_cache = redis_instance.get(f'currentEquipmentInfo:{contract_code}')
            if redis_contract_cache:
                result = json.loads(redis_contract_cache)
            else:
                header = request.headers
                app_id = header['App-Id']
                app_user_token = header['App-User-Token']
                data_token = getUserAuthSessionData(header['Authorization'])

                app_user_token_validator = AppUserTokenValidator()
                token_decrypt = app_user_token_validator.validateAppUserTokenAndAppId(app_user_token, app_id)
                data_token = {**data_token, **token_decrypt}

                base_env = project_settings.APP_ENVIRONMENT

                # Đăng nhập lấy token
                if base_env == 'local':
                    proxies = {}
                else:
                    proxies = {
                        "http": "http://proxy.hcm.fpt.vn:80",
                        "https": "http://proxy.hcm.fpt.vn:80"
                    }
                headers = {
                    'Authorization': 'Basic aW5zaWRlLWFwaTpGdGVsaXNjQDEyMw=='
                }
                response = utils.call_api(
                    host=INSIDE_CONFIG['CONTRACT_INFO_EQUIPMENT'][base_env],
                    func=INSIDE_CONFIG['CONTRACT_INFO_EQUIPMENT']['generate_token']['func'],
                    method=INSIDE_CONFIG['CONTRACT_INFO_EQUIPMENT']['generate_token']['method'],
                    headers=headers,
                    proxies=proxies
                )

                # Có token rồi thì truyền vào header cho api để lấy ds hiện trạng
                headers['Authorization'] = 'Bearer ' + response.replace('"', '')
                payload = {
                    'contract': contract_code
                }
                response = utils.call_api(
                    host=INSIDE_CONFIG['CONTRACT_INFO_EQUIPMENT'][base_env],
                    func=INSIDE_CONFIG['CONTRACT_INFO_EQUIPMENT']['get_info_by_contract_TIN_PNC']['func'],
                    method=INSIDE_CONFIG['CONTRACT_INFO_EQUIPMENT']['get_info_by_contract_TIN_PNC']['method'],
                    params=payload,
                    headers=headers,
                    proxies=proxies
                )
                data = json.loads(response)
                if data['Code'] == 12:
                    return response_data(result, status=gb.STATUS_CODE_INVALID_INPUT,
                                         message='Mã hợp đồng không tồn tại')
                elif data['Code'] == 200:
                    if data['Data']:
                        result['internetPackages'] = [{
                            'id': 0,
                            'name': item['Name'].strip(),
                            'quantity': int(item['Quantity']),
                            'downloadSpeed': int(item['DownloadSpeed']),
                            'uploadSpeed': int(item['UploadSpeed'])
                        } for item in data['Data']['InternetPackages']]
                        result['routers'] = [{
                            'id': 0,
                            'name': item['Name'].strip(),
                            'quantity': int(item['Quantity']),
                            'wifi': int(item['Wifi']),
                            'LANWifi': int(item['LANWifi']),
                            # 'wifi24Pow': int(item['Wifi24Pow']),
                            # 'wifi5Pow': int(item['Wifi5Pow'])
                            'wifi24Pow': None,
                            'wifi5Pow': None
                        } for item in data['Data']['Routers']]
                        result['accessPoints'] = [{
                            'id': 0,
                            'name': item['Name'].strip(),
                            'quantity': int(item['Quantity']),
                            'wifi': int(item['Wifi']),
                            'LANWifi': int(item['LANWifi']),
                            # 'wifi24Pow': int(item['Wifi24Pow']),
                            # 'wifi5Pow': int(item['Wifi5Pow'])
                            'wifi24Pow': None,
                            'wifi5Pow': None
                        } for item in data['Data']['AccessPoint'] if data['Data']['AccessPoint'][0]['Name'] is not None]

                        result['totalAP'] = len(data['Data']['AccessPoint'])
                        result['regions'] = data['Data']['Regions'].strip()
                        result['branchFullName'] = data['Data']['BranchFullName'].strip()

                        redis_instance.set(f'currentEquipmentInfo:{contract_code}',
                                           json.dumps(result), int(get_second_now_to_end_day()))

                        data_log = {**result, **data_token, 'sdkUserId': data_token['userId'],
                                    'sdkAccUsername': data_token['accUsername'], 'contractCode': request.contract_code}

                        try:
                            serializer = CurrentContractInfoLogSerializer(data=data_log)
                            if serializer.is_valid():
                                serializer.save()
                            else:
                                print('Error/Loi: ', str(serializer.errors))
                        except Exception as ex:
                            print('Error/Loi: ', str(ex))

                    else:
                        return response_data(result, status=gb.STATUS_CODE_FAILED,
                                             message='Không lấy được thông tin hợp đồng!!!')
        except Exception as ex:
            print("Error/Loi: " + str(ex))
            return response_data(None, gb.STATUS_CODE_FAILED, gb.MESSAGE_API_ERROR_LOGIC)
        return response_data(result, message=gb.MESSAGE_API_SUCCESS)

    def decode_image_base64(self, request, *args, **kwargs):
        try:
            request_data = request.data
            image = None
            if int(request_data['key']) == 1:
                image = base64.b64decode(request_data['imageOrigin'])
            else:
                image = base64.b64decode(request_data['imageResult'])

            # Set the content-type header so the client knows what type of data is being returned
            # response.headers['Content-Type'] = 'image/jpeg'

            # Return the raw binary data of the response directly
        except Exception as ex:
            print('Error/Loi: ', ex)
            return response_data(status=gb.STATUS_CODE_FAILED, message=gb.MESSAGE_API_ERROR_LOGIC)
        return HttpResponse(image, content_type='image/jpeg')

    # def test_api(self, request):
    #     try:
    #         base_env = project_settings.APP_ENVIRONMENT
    #         response_sdk_users = utils.call_api(
    #             host=SERVICE_CONFIG['CHM_AUTH'][base_env],
    #             func=SERVICE_CONFIG['CHM_AUTH']['test_api']['func'],
    #             method=SERVICE_CONFIG['CHM_AUTH']['test_api']['method'],
    #         )
    #         data_sdk_users = json.loads(response_sdk_users)['data']
    #         data_email = [item['acc_username'].lower() for item in data_sdk_users]
    #
    #         payload_info_user = {
    #             'list_email': data_email
    #         }
    #         response_info_user = utils.call_api(
    #             host=SERVICE_CONFIG['PROFILE'][base_env],
    #             func=SERVICE_CONFIG['PROFILE']['info_child_depart_for_email']['func'],
    #             method=SERVICE_CONFIG['PROFILE']['info_child_depart_for_email']['method'],
    #             data=payload_info_user
    #         )
    #         print(response_info_user)
    #         data_info_user = json.loads(response_info_user)['data']
    #
    #     except Exception as ex:
    #         print(f'Error/Loi: {ex}')
    #         return response_data(None, 0, 'Lỗi rồi')
    #     return response_data(data_info_user)
