from Cryptodome.Cipher import AES
import math, sys, os
import string
import random
import base64
import json
from Crypto.Util.Padding import pad
from datetime import datetime, timedelta, date
from ..entities.centralized_session import CentralizedSession
from app.core.helpers.global_variable import *
from app.core.helpers.helper import *

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


def is_none(v):
    if v is None:
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


def empty(_val):
    if _val in ({}, [], None, '', 0):
        return True
    if isinstance(_val, str) and len(_val.strip()) == 0:
        return True
    return False


def moneyFormat(_num, unit=''):
    _str = "{:,}{}".format(_num, unit)
    return _str


def numberFormat(_num):
    _str = '0'
    if (isinstance(_num, int) or isinstance(_num, float)):
        if (_num < 0):
            _str = "({:,})".format(_num)
            _str = str.replace(_str, '-', '')
        else:
            _str = "{:,}".format(_num)
    else:
        try:
            _str = str(_num)
        except:
            _str = "0"
    return _str


def getSalaryObj(_item, _value_list, _index='0'):
    details = []
    index = _index
    if not empty(_item['details']):
        i = 1
        if index == '0':
            index = ''
        else:
            index = '{}.'.format(index)
        for item in _item['details']:
            _childIndex = "{}{}".format(index, i)
            details.append(getSalaryObj(item, _value_list, _childIndex))
            i += 1
    number = 0
    insideId = _item['info']['insideId']
    if empty(insideId):
        if not empty(_item['info'].get('formula', '')):
            formula = _item['info'].get('formula', '')
            if not empty(formula):
                if 'sum' in formula:
                    sumList = formula['sum']
                    for key in sumList:
                        if isinstance(key, float) or isinstance(key, int):
                            number += key
                        elif type(key) == str:
                            if not empty(_value_list[key]):
                                valueNum = _value_list[key].get('value', 0)
                                if isinstance(key, int):
                                    valueNum = int(valueNum)
                                elif isinstance(key, float):
                                    valueNum = float(valueNum)
                                else:
                                    try:
                                        valueNum = int(valueNum)
                                    except Exception as sumex:
                                        print("[ERROR] key={} as errror={}".format(key, sumex))
                                        valueNum = 0
                                number += valueNum
                if 'multiply' in formula:
                    if number == 0:
                        number = 1
                    multiplyList = formula['multiply']
                    for key in multiplyList:
                        if isinstance(key, float) or isinstance(key, int):
                            number *= key
                        else:
                            try:
                                if (not empty(_value_list[key])):
                                    number *= _value_list[key].get('value', 1)
                            except Exception as ee:
                                print("{}".format(ee))
                    number = math.floor(number)
    else:
        number = _value_list[insideId].get('value', 0)
    formatFloat = _item['info'].get('formatFloat', '')
    if empty(formatFloat):
        number = numberFormat(number)
    else:
        try:
            number = formatFloat.format(number)
        except:
            number = numberFormat(number)
    return {
        "index": "{}".format(_index),
        "id": _item['info']['myptId'],
        "title": _item['info']['myptName'],
        "number": number,
        "info": "",
        "details": details
    }


def getSalaryObjFromDB(_decodeKey, _item, _value_list, _index='0'):
    details = []
    index = _index
    if (not empty(_item['details'])):
        i = 1
        if (index == '0'):
            index = ''
        else:
            index = '{}.'.format(index)
        for item in _item['details']:
            _childIndex = "{}{}".format(index, i)
            details.append(getSalaryObjFromDB(_decodeKey, item, _value_list, _childIndex))
            i += 1
    number = 0
    valueId = _item['info']['dbColumn']
    try:
        if (empty(valueId)):
            if (not empty(_item['info'].get('formula', ''))):
                formula = _item['info'].get('formula', '')
                if (not empty(formula)):
                    if ('sum' in formula):
                        sumList = formula['sum']
                        for key in sumList:
                            if (isinstance(key, float) or isinstance(key, int)):
                                number += key
                            elif (type(key) == str):
                                if (not empty(_value_list[key])):
                                    valueNum = decrypt_aes(_decodeKey, _value_list[key])
                                    if (isinstance(key, int)):
                                        valueNum = int(valueNum)
                                    elif (isinstance(key, float)):
                                        valueNum = float(valueNum)
                                    else:
                                        try:
                                            valueNum = str.replace(valueNum, ',', '')
                                            valueNum = int(valueNum)
                                        except:
                                            print("ERRROR decrypt_aes {} {} = {}".format(_decodeKey, _value_list[key],
                                                                                         valueNum))
                                            valueNum = 0
                                    number += valueNum

        else:
            if (not empty(_value_list[valueId])):
                number = decrypt_aes(_decodeKey, _value_list[valueId])
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("[ERROR] getSalaryObjFromDB {} {} {} {}".format(ex, exc_type, fname, exc_tb.tb_lineno))
        number = 0
    if (empty(number)):
        number = 0
    if (not (isinstance(number, float) or isinstance(number, int))):
        try:
            number = int(number)
        except:
            try:
                number = float(number)
            except Exception as ex:
                print("[ERROR] getSalaryObjFromDB number convert error {} type {}".format(number, type(number)))
    return {
        "index": "{}".format(_index),
        "id": _item['info']['myptId'],
        "title": _item['info']['myptName'],
        "number": numberFormat(number),
        "info": "",
        "details": details
    }


def getSalaryEmptyObj(_item, _level=0, _index='0'):
    details = []
    index = _index
    if _level < SALARY_MAX_LEVEL_EMPTY_VALUE:
        _level += 1
        if not empty(_item['details']):
            i = 1
            if index == '0':
                index = ''
            else:
                index = '{}.'.format(index)
            for item in _item['details']:
                _childIndex = "{}{}".format(index, i)
                details.append(getSalaryEmptyObj(item, _level, _childIndex))
                i += 1
    return {
        "index": "{}".format(_index),
        "id": _item['info']['myptId'],
        "title": _item['info']['myptName'],
        "number": '0',
        "info": "",
        "details": details
    }
    
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
            host=SERVICE_CONFIG["logs"][app_env],
            func=SERVICE_CONFIG["logs"]["save_log"]["func"],
            method=SERVICE_CONFIG["logs"]["save_log"]["method"],
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
