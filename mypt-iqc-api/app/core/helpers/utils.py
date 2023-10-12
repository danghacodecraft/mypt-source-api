import ast
import os
import time
import concurrent.futures
import re
import requests
from Cryptodome.Cipher import AES
import string
import random
import base64
from Crypto.Util.Padding import pad
from rest_framework.utils import json
from ..entities.centralized_session import CentralizedSession
from datetime import datetime, timedelta, date
from core.helpers.iqc_global_variable import VIEW_IMAGE_AUTH_PUBLIC, url_img
from ...configs import app_settings
from core.helpers import auth_session_handler as authSessionHandler

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


def is_null_or_empty(_str):
    if is_none(_str):
        return True
    if isinstance(_str, str):
        if is_empty(_str):
            return True
        if len(_str.strip()) > 0:
            return _str.strip().isspace()
        return True
    return False


def empty(_val):
    if _val in ({}, [], None, '', 0):
        return True
    if isinstance(_val, str) and len(_val.strip()) == 0:
        return True
    return False


def is_none(v):
    if v is None:
        return True
    return False


def empty(_val):
    if _val in ({}, [], None, '', 0):
        return True
    if isinstance(_val, str) and len(_val.strip()) == 0:
        return True
    return False


def is_empty(_str):
    if isinstance(_str, str):
        return is_none(_str) or len(_str.strip()) == 0
    return False


def get_current_datetime():
    return datetime.utcnow() + timedelta(hours=7)


def get_str_datetime_now_import_db():
    time_now = get_current_datetime()
    return time_now.strftime('%d/%m/%Y %H:%M:%S')


def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        params = kwargs.pop("params", None)
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        proxies = kwargs.pop("proxies", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data) if data else None
        response = requests.request(method,
                                    host + func,
                                    params=params,
                                    headers=headers,
                                    data=payload,
                                    proxies=proxies
                                    )
        # print("====> DATA CALL: ", response.text)
        print(type(response))
        print(type(response.text))
        print(response)

        return response.text.replace('"', '\"')
    except Exception as ex:
        print("{} >> Error/Loi: {}".format("call_api", ex))
        return ex


def call_api_method_get(**kwargs):
    try:
        host = kwargs.pop("host")
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        params = kwargs.pop("params")

        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn",
        }
        response = requests.get(url=host, params=params, headers=headers, proxies=proxies)
        result = response.text
        return json.loads(result)
    except Exception as ex:
        print(str(ex))
        return None


def call_api_method_post(**kwargs):
    try:
        host = kwargs.pop("host")
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        data = kwargs.pop("json")

        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn",
        }
        response = requests.post(host, json=data, headers=headers, proxies=proxies)
        result = response.text
        return json.loads(result)
    except Exception as ex:
        print(str(ex))
        return None


def convert_no_accent_vietnamese(text, fname=""):
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """
    new_text = ""
    try:
        patterns = {
            '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
            '[đ]': 'd',
            '[èéẻẽẹêềếểễệ]': 'e',
            '[ìíỉĩị]': 'i',
            '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
            '[ùúủũụưừứửữự]': 'u',
            '[ỳýỷỹỵ]': 'y',
            '[ ]': "_"
        }
        if not is_null_or_empty(text):
            output_init = text.strip()
            output = output_init.lower()
            for regex, replace in patterns.items():
                output = re.sub(regex, replace, output)
                # deal with upper case
                output = re.sub(regex.upper(), replace.lower(), output)
                new_text = output
    except Exception as e:
        print(e)
        # logger.info("convert_no_accent_vietnamese >> {} Error/Loi : {}".format(fname, e))
    return new_text


def revert_link_image(request, _link):
    user_token = authSessionHandler.get_user_token(request)
    user_id = user_token.get("userId", "")
    path = encrypt_aes(app_settings.AES_SECRET_KEY, f'{url_img}{_link};{user_id}')
    return VIEW_IMAGE_AUTH_PUBLIC + path


def decode_link_image(_link):
    if "path" not in _link:
        return _link

    private_path = _link.replace(VIEW_IMAGE_AUTH_PUBLIC, "")
    try:
        public_path = decrypt_aes(app_settings.AES_SECRET_KEY, private_path)
        tokens = public_path.split(';')
        if not tokens[0]:
            return _link
        return tokens[0].replace(url_img, "")
    except Exception as ex:
        print(f'[{datetime.now()}][decode_link_image] >> {ex}')
        return _link


def decode_link_images(images=None):
    if images is None:
        return []
    else:
        futures = []
        data_result = []
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     for image in images:
        #         future = executor.submit(decode_link_image, image)
        #         futures.append(future)
        for image in images:
            future = decode_link_image(image)
            futures.append(future)
            data_result.append(future)
        # for future in futures:
        #     data_result.append(future.result())
        return data_result

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
        if json.loads(response)["statusCode"] == 1:
            print(f"Time save log cho api {api_name}: {datetime.now()}")
            print("Success!")
    except Exception as ex:
        print("Call api error: " + str(ex))
