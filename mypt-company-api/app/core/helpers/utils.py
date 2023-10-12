from datetime import *
from Cryptodome.Cipher import AES
import string
import random
import base64
from Crypto.Util.Padding import pad
from ..entities.centralized_session import CentralizedSession
import json
import requests
from ...configs.variable import *

# GHI LOG
from ...configs.service_api_config import *
from django.conf import settings as project_settings

def aes256():
    try:
        # 16s bit
        BS = 16
        # SECRET KEY of API SCM in Document
        # Staging
        # key =   b'8840240ce0ecbb703a9425b40a121d99'
        # Production
        key = b'33b8ddca078f4bbc85d90fb7d3b4fde4'
        # Key IV of API SCM in Document
        iv =  b'bscKHn8REOJ2aikS'
        return BS,key,iv
    except Exception as e:
        print(e)


def randomSecretKey(stringLength=16, fname=""):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


def encrypt_aes(iv, raw, fname=""):
    # BS = aes256()[0]
    key = aes256()[1]
    _iv = iv.encode()
    # pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    # raw = pad(raw)
    raw = pad(raw.encode(), 16)
    cipher = AES.new(key, AES.MODE_CBC, _iv)
    return base64.b64encode(cipher.encrypt(raw)).decode("utf-8")


def decrypt_aes(iv, enc, fname=""):
    key = aes256()[1]
    # iv = aes256()[2]
    unpad = lambda s : s[:-ord(s[len(s)-1:])]
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC, iv.encode() )
    return unpad(cipher.decrypt( enc )).decode("utf-8")

def get_data_from_token(request):
    try:
        headerAuthToken = request.headers.get("Authorization")
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        redisObj = CentralizedSession()
        dataRedis = redisObj.validateSession(newHeaderAuthToken)
        return dataRedis['sessionData']
    except:
        return None

def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        response = requests.request(method, host+func, headers=headers, data=payload)
        return response.text
    except Exception as ex:
        print("Call api error: " + str(ex))
        return None
        
def call_api_https(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        proxies = { 
            "http"  : "http://proxy.hcm.fpt.vn:80", 
            "https" : "http://proxy.hcm.fpt.vn:80"
        }
        response = requests.request(method, host+func, headers=headers, data=payload, proxies=proxies)
        return response.text
    except Exception as ex:
        print("Call_api_https error:", ex)
        return None



def call_other_service_api(**kwargs):
    try:
        app_env = "base_http_" + config('APP_ENV')
        service_call = kwargs.pop("service_call")
        end_point = kwargs.pop('end_point')
        host = SERVICE_CONFIG[service_call][app_env]
        func = SERVICE_CONFIG[service_call][end_point]['func']
        method = SERVICE_CONFIG[service_call][end_point]['method']
        data = kwargs.pop("data", None)
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(data)
        response = requests.request(method, host + func, headers=headers, data=payload)

        data = response.text
        data = json.loads(data)
        return data['data']
    except Exception as ex:
        print(f'Call other service api error', ex)
        return None
        
def date_from_now(d=0):
    data_time = datetime.now()
    data_time += timedelta(days=d)
    return data_time.strftime(DATE_FORMAT_QUERY)

def date_from_now_mobile(d=0):
    data_time = datetime.now()
    data_time += timedelta(days=d)
    return data_time.strftime(DATE_FORMAT)

def month_from_now(m=0):
    if m == 0:
        return datetime.now().replace(day=1).strftime(DATE_FORMAT_QUERY), datetime.now().strftime(DATE_FORMAT_QUERY)
    lastMonth = datetime.now()
    for item in range(m):
        lastMonth = lastMonth.replace(day=1)
        lastMonth = lastMonth - timedelta(days=1)
    lastMonth = lastMonth.replace(day=1)
    return lastMonth.strftime(DATE_FORMAT_QUERY), datetime.now().strftime(DATE_FORMAT_QUERY)

def to_str_fr_list(_list):
    if isinstance(_list, list):
        return ';'.join([str(item) for item in _list])
    
    
# GHI LOG
def api_save_log(request, data_input=None, data_output=None, api_status=1, err_analysis=1, api_name="", status_code=1, message="Success", data_detail=None, jsonParamsRequired=None, action_type=None):
    app_env = "base_http_" + project_settings.APP_ENVIRONMENT
    try:
        result = {}
        result = {
            "statusCode": status_code,
            "message": message,
            "data": data_output
        }
        if data_input is not None:
            data_input = str(data_input)
        if data_detail is not None:
            data_detail = str(data_detail)
        if action_type is not None:
            actionCode = SERVICE_CONFIG_SAVE_LOGS_API[api_name]["action_code"][action_type]
        else:
            actionCode = SERVICE_CONFIG_SAVE_LOGS_API[api_name]["action_code"]
            
        response = call_api(
            host=SERVICE_CONFIG["logs_api"][app_env],
            func=SERVICE_CONFIG["logs_api"]["save_log"]["func"],
            method=SERVICE_CONFIG["logs_api"]["save_log"]["method"],
            headers={
                "Authorization": request.headers.get("Authorization"),
                "Content-Type": "application/json"
            },
            data={
                "dataInput": data_input,
                "dataOutput": result,
                "dataDetail": data_detail,
                "apiUri": request.META.get("HTTP_HOST", "") + request.META.get("PATH_INFO", ""),
                "jsonParamsRequired": jsonParamsRequired,
                "apiStatus": api_status,
                "errAnalysis": err_analysis,
                "apiRoute": SERVICE_CONFIG_SAVE_LOGS_API["service_name"] + SERVICE_CONFIG_SAVE_LOGS_API[api_name]["func"],
                "functionCode": SERVICE_CONFIG_SAVE_LOGS_API[api_name]["function_code"],
                "actionCode": actionCode
            }
        )
        if json.loads(response)["statusCode"]:
            print(f"Time save log cho api {api_name}: {datetime.now()}")
            print("Success!")
    except Exception as ex:
        print("Call api error: " + str(ex))
