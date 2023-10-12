import base64
import math
import os
import random
import string
import sys
import json
from datetime import datetime

from Crypto.Util.Padding import pad
from Cryptodome.Cipher import AES

from profile_app.core.helpers.global_data import *
from ..entities.centralized_session import CentralizedSession

# GHI LOG
from ...configs.service_api_config import *
from ...core.helpers.service_api import *
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
        iv = b'bscKHn8REOJ2aikS'
        return BS, key, iv
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
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC, iv.encode())
    return unpad(cipher.decrypt(enc)).decode("utf-8")


def get_email_from_token(request):
    try:
        headerAuthToken = request.headers.get("Authorization")
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        redisObj = CentralizedSession()
        dataRedis = redisObj.validateSession(newHeaderAuthToken)
        return dataRedis['sessionData']['email']
    except:
        return None


def is_empty(_val):
    if _val in ({}, [], None, '', 0):
        return True
    if isinstance(_val, str) and len(_val.strip()) == 0:
        return True
    return False


def convert_date_export(__date, fname=""):
    result = ""
    try:
        if __date is not None:
            result = datetime.strftime(__date, "%d/%m/%Y")

            result_split = result.split("/")
            if len(result_split[0]) == 1:
                result = "0" + result_split[0] + "/" + result_split[1] + result_split[2]
        else:
            result = str(__date)
    except Exception as e:
        print("{}: {}".format(fname, e))
    return result

# GHI LOG
def api_save_log(request, data_input=None, data_output="", api_status=1, err_analysis=1, api_name="", status_code=1, message="Success", data_detail=None, jsonParamsRequired=None, action_type=None):
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
