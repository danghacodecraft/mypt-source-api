import ast
import json

import redis
from django.conf import settings as project_settings
from django.http import JsonResponse

from app.configs import app_settings
from app.core.entities.app_user_token_validator import AppUserTokenValidator
from app.core.entities.my_rsa_alogrithm import MyRSA
from app.core.helpers import global_variable as gb
from app.core.helpers import utils as utHelper
from app.core.helpers.response import json_response_data


class ContractCodeValidateMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        middleware_applied = False
        request.contract_code = None
        cur_url = request.path
        class_name = self.__class__.__name__.lower()
        routes_middleware_data = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(class_name)

        if cur_url in routes_middleware_data:
            middleware_applied = True

        if middleware_applied:
            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                              , port=project_settings.REDIS_PORT_CENTRALIZED
                                              , db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                              password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                              , decode_responses=True, charset='utf-8')
            data_rsa_chm = ast.literal_eval(redisInstance.get('appsRSAKeys'))
            try:
                appId = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, request.headers.get('App-Id'))
            except Exception as ex:
                print(str(ex))
                appId = ''
            if appId == '':
                return json_response_data(None, status=3, message='Thiếu App-Id')
            data_rsa_chm = data_rsa_chm[appId]

            my_rsa = MyRSA()

            public_key, private_key = my_rsa.loading_key_rsa(data_rsa_chm['publicKey'], data_rsa_chm['privateKey'])

            content_type = request.content_type
            try:
                if content_type == 'application/json':
                    data = json.loads(request.body)
                    if 'contractCode' not in data:
                        return json_response_data(None, status=gb.STATUS_CODE_INVALID_INPUT,
                                                  message='Thiếu contractCode')
                    else:
                        data = data['contractCode']
                        request.contract_code = my_rsa.decrypt(data, private_key).upper().strip()
                        if len(request.contract_code) < 9:
                            return json_response_data(None, status=gb.STATUS_CODE_INVALID_INPUT,
                                                      message='Mã hợp đồng phải từ 9 chữ số')
                elif content_type == 'multipart/form-data':
                    if 'contractCode' not in request.POST:
                        return json_response_data(None, status=gb.STATUS_CODE_INVALID_INPUT,
                                                  message='Mã hợp đồng phải từ 9 chữ số')
                    else:
                        data = request.POST['contractCode']
                        request.contract_code = my_rsa.decrypt(data, private_key).upper().strip()
                        if len(request.contract_code) < 9:
                            return json_response_data(None, status=gb.STATUS_CODE_INVALID_INPUT,
                                                      message='Mã hợp đồng phải từ 9 chữ số')
            except Exception as ex:
                return json_response_data(None, status=gb.STATUS_CODE_ERROR_LOGIC,
                                          message=str(ex))
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_request(self, request):
        print('vao process request')
        return None

    def process_response(self, request, response):
        print('vao process response')

        return None
