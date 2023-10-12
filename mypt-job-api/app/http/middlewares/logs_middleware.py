from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
import json
from ...configs.variable_system import function_code, action_code
from ...configs.service_api_config import *
import requests
from ...configs.variable_system import NO_PROXY, HEADERS_DEFAULT,STATUS_TOOLS, EXPIRE_TOOL_STATUS,TAB_TOOLS_CONDITION



class APILoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            condition = response.__dict__.get('data', {}).get("statusCode", "NO_LOG")
            current_url = resolve(request.path_info).route
            if condition == "NO_LOG":
                return response
            if current_url in set(function_code.keys()):
                data_log = {
                    "apiRoute":str(request.path_info),
                    "functionCode": function_code.get(str(current_url), ""),
                    "actionCode": action_code.get(str(current_url), ""),
                    "dataInput": str(request.META['QUERY_STRING']) if request.method == 'GET' else str(json.loads(request.body.decode("utf-8"))),
                    "dataOutput": {},
                    "jsonParamsRequired": None,
                    "apiUri": "http://"+request.META["HTTP_HOST"]+request.path_info,
                    "apiStatus": response.__dict__.get('data', {}).get("statusCode", 0),
                    "errAnalysis": 1 if response.__dict__.get('data', {}).get("statusCode", 0) != 0 else -1
                }
                result = requests.request(
                    **get_api_info("logs", "save_log"),
                    data=data_log,
                    headers=HEADERS_DEFAULT.update({
                        "Authorization": str(request.META.get("HTTP_AUTHORIZATION", ""))
                    })
                )
        except Exception as exc:
            print("APILoggingMiddleware: ", exc)
            return response
        return response
