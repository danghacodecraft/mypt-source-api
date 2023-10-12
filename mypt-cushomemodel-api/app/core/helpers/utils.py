import base64
import json
import random
import string
import tempfile
from datetime import datetime, timedelta

import requests
from Crypto.Util.Padding import pad
from Cryptodome.Cipher import AES
from django.conf import settings as project_settings

from .global_variable import *
from ...configs.service_api_config import SERVICE_CONFIG


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


def get_current_datetime():
    return datetime.utcnow() + timedelta(hours=7)


def get_str_datetime_now_import_db():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime(DATETIME_FORMAT)
    return str_time_now


def encrypt_server(iv, raw, fname=""):
    try:
        # BS = aes256()[0]
        key = aes256()[1]
        _iv = iv.encode()
        # pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        # raw = pad(raw)
        raw = pad(raw.encode(), 16)
        cipher = AES.new(key, AES.MODE_CBC, _iv)
        return base64.b64encode(cipher.encrypt(raw)).decode("utf-8")
    except Exception as e:
        print("{}: {}".format(fname, e))


def call_api(**kwargs):
    try:
        host = kwargs.pop('host')
        func = kwargs.pop('func')
        params = kwargs.pop('params', None)
        method = kwargs.pop('method')
        data = kwargs.pop('data', None)
        proxies = kwargs.pop('proxies', None)
        headers = kwargs.pop('headers', {'Content-Type': 'application/json'})
        payload = json.dumps(data) if data else None
        response = requests.request(method,
                                    host + func,
                                    params=params,
                                    headers=headers,
                                    data=payload,
                                    proxies=proxies
                                    )
        # print(response.text)
        # print('====> DATA CALL: ', response)
        return response.text.replace('"', '\"')
    except Exception as ex:
        print('{} >> Error/Loi: {}'.format('call_api', ex))
        return ex


# trả về id hoặc code trong enum
def return_choice_id_or_code(value, list_choice):
    for choice in list_choice:
        if choice[1].lower() == value.lower():
            return choice[0]
    return None


# trả về name trong enum
def return_choice_name(value, list_choice):
    for choice in list_choice:
        if choice[0] == value:
            return choice[1]


def save_link_simulate_wifi_2d(image_original, image_wifi24, image_wifi5):
    base_env = project_settings.APP_ENVIRONMENT
    url = SERVICE_CONFIG['HO_MEDIA'][base_env] + SERVICE_CONFIG['HO_MEDIA']['upload_file_private']['func']

    image_original_decode = base64.b64decode(image_original)
    image_wifi24_decode = base64.b64decode(image_wifi24)
    image_wifi5_decode = base64.b64decode(image_wifi5)

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_original_file:
        image_original_file.write(image_original_decode)
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_wifi24_file:
        image_wifi24_file.write(image_wifi24_decode)
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_wifi5_file:
        image_wifi5_file.write(image_wifi5_decode)

    payload_original = {'folder': '/cushomemodel/contract_original_images/',
                        'userEmail': 'longthk',
                        'numberFile': '1'}
    payload_simulate = {'folder': '/cushomemodel/contract_heatmap_images/',
                        'userEmail': 'longthk',
                        'numberFile': '1'}

    file_image_original = {
        'file_1': ('image_original.jpg', open(image_original_file.name, 'rb'), 'image/jpeg')
    }
    file_image_wifi24 = {
        'file_1': ('image_wifi24.jpg', open(image_wifi24_file.name, 'rb'), 'image/jpeg')
    }
    file_image_wifi5 = {
        'file_1': ('image_wifi5.jpg', open(image_wifi5_file.name, 'rb'), 'image/jpeg')
    }

    link_image_original = requests.post(url, data=payload_original, files=file_image_original)
    link_image_wifi24 = requests.post(url, data=payload_simulate, files=file_image_wifi24)
    link_image_wifi5 = requests.post(url, data=payload_simulate, files=file_image_wifi5)

    link_image_original = json.loads(link_image_original.text.replace('"', '\"'))
    link_image_wifi24 = json.loads(link_image_wifi24.text.replace('"', '\"'))
    link_image_wifi5 = json.loads(link_image_wifi5.text.replace('"', '\"'))
    result = {
        'image': link_image_original['data']['linkFile'][0],
        'wifi24Image': link_image_wifi24['data']['linkFile'][0],
        'wifi5Image': link_image_wifi5['data']['linkFile'][0]
    }
    return result


def save_link_image_model_2d(image_original):
    base_env = project_settings.APP_ENVIRONMENT
    url = SERVICE_CONFIG['HO_MEDIA'][base_env] + SERVICE_CONFIG['HO_MEDIA']['upload_file_private']['func']

    image_original_decode = base64.b64decode(image_original)

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_original_file:
        image_original_file.write(image_original_decode)

    payload_original = {'folder': '/cushomemodel/contract_original_images/',
                        'userEmail': 'longthk',
                        'numberFile': '1'}

    file_image_original = {
        'file_1': ('image_original.jpg', open(image_original_file.name, 'rb'), 'image/jpeg')
    }

    link_image_original = requests.post(url, data=payload_original, files=file_image_original)

    link_image_original = json.loads(link_image_original.text.replace('"', '\"'))
    result = {
        'image': link_image_original['data']['linkFile'][0],
    }
    return result


def process_equipment_data(data, survey_id, modem_rule, **kwargs):
    equipment_list = []
    if isinstance(data, list):
        for item in data:
            item['idEquipment'] = item.get('id', 0)
            item['modelSurveyId'] = survey_id
            item['modemRule'] = modem_rule
            item['modelType'] = kwargs.get('model_type')
            equipment_list.append(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in ('model', 'other'):
                equipment_list.extend(process_equipment_data(value, survey_id, modem_rule, model_type=key))
            else:
                equipment_list.extend(process_equipment_data(value, survey_id, modem_rule, model_type='model'))
    return equipment_list




