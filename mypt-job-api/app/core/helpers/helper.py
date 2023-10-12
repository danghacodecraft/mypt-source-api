import datetime
from dateutil.parser import parse
import re
from ast import literal_eval
import base64
import json
import requests
from dateutil.relativedelta import relativedelta


# '2021-06-02T09:14:43Z'
def get_date(date_time=None):
    if date_time is None:
        print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.date()
    except:
        print('ngày tháng không đúng định dạng')
        return ""


def get_time(date_time=None):
    if date_time is None:
        print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.time()
    except:
        print('ngày tháng không đúng định dạng')
        return ""


def convert_vi_to_en(s):
    try:
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
        s = re.sub(r'[Đ]', 'D', s)
        s = re.sub(r'[đ]', 'd', s)
        return s
    except:
        return str


def base64_decode_array(str):
    base64_bytes = base64.b64decode(str)
    base64_string = base64_bytes.decode("ascii")
    base64_data = literal_eval(base64_string)
    return base64_data


def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        proxies = kwargs.pop("proxies", {
            'http': None,
            'https': 'proxy.hcm.fpt.net'
        })
        payload = json.dumps(data)
        response = requests.request(method, host + func, headers=headers, data=payload, proxies=proxies)
        if response.status_code == 200:
            return json.loads(response.text)
        raise ValueError("Gọi data không thành công!")
    except Exception as ex:
        print(f"{datetime.datetime.now()} >> call_api >> {ex}")
        return None


def check_data_with_re(pattern, data):
    if re.search(pattern, data):
        return True
    return False


def change_date_format(dt):
    return re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', dt)


def check_valid_date(date, date_format):
    try:
        datetime.datetime.strptime(date, date_format[0])
        return True
    except ValueError:
        return False


def convert_string_date(date, date_format):
    return datetime.datetime.strptime(str(date), date_format[0])


def format_number(num):
    if str(num).endswith(".0") or str(num).endswith(".00"):
        return int(num)
    else:
        return num


def last_day_of_month(any_day):
    return (any_day + relativedelta(day=31))


def validate_str_datetime(datetime_text):
    try:
        if datetime_text != datetime.strptime(datetime_text, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'):
            raise ValueError
        return True
    except ValueError:
        return False


def snake_to_camel(s):
    parts = s.lower().split('_')
    return parts[0] + ''.join(x.capitalize() for x in parts[1:])

def keys_snake_to_camel(input_list_of_dicts):
    camel_list = []
    for input_dict in input_list_of_dicts:
        camel_dict = {}
        for key, value in input_dict.items():
            camel_key = snake_to_camel(key)
            camel_dict[camel_key] = value
        camel_list.append(camel_dict)
    return camel_list
