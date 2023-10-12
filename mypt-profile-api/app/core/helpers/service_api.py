from ...configs.service_api_config import *
from django.conf import settings as project_settings
import json
import requests
from django.core.cache import cache


def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        response = requests.request(method, host + func, headers=headers, data=payload)
        return response.text
    except Exception as ex:
        print("{} >> Error/Loi: {}".format("call_api", ex))
        return str(ex)


def hr_auth():
    if cache.has_key('hrlogin'):
        return cache.get('hrlogin')
    payload = {
        "username": "",
        "password": ""
    }

    headers = {
        'Abp-TenantId': '1',
        'Content-Type': 'application/json'
    }

    response = call_api(
        host=SERVICE_CONFIG['hr']['base_http'],
        func=SERVICE_CONFIG['hr']['auth'],
        method=SERVICE_CONFIG['hr']['method'],
        headers=headers,
        data=payload
    )
    dataApi = json.loads(response)
    cache.set('hrlogin', dataApi['authorization'], timeout=dataApi['expireInSeconds'])
    return dataApi['authorization']


def get_employee_info_from_hris(token="", email=""):
    payload = {
        "email": email
    }

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    response = call_api(
        host=SERVICE_CONFIG['hr']['base_http'],
        func=SERVICE_CONFIG['hr']['GetEmployeeInfo'],
        method=SERVICE_CONFIG['hr']['method'],
        headers=headers,
        data=payload
    )

    dataApi = json.loads(response)
    return dataApi


def get_salary_in_home(request):
    app_env = project_settings.APP_ENVIRONMENT
    base_http = "base_http_" + app_env
    url = SERVICE_CONFIG["job-api"][base_http] + SERVICE_CONFIG["job-api"]["get_salary_in_home"]["func"]
    method = SERVICE_CONFIG["job-api"]["get_salary_in_home"]["method"]

    response = requests.request(method, url,
                                headers={'Content-Type': 'application/json',
                                         'Authorization': request.headers.get('Authorization', '')})
    if response.status_code == 200:
        return json.loads(response.text)
    return None
