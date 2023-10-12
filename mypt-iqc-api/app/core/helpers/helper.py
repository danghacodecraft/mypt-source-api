import datetime
import re

from dateutil.parser import parse
import re
from ast import literal_eval
import base64
from dateutil.relativedelta import relativedelta

format_from = "%Y-%m-%dT%H:%M:%S.%f%z"
format_to = "%d/%m/%Y %H:%M:%S"


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


def format_date_time(time_data, _format_from=format_from, _format_to=format_to):
    try:
        date_time = datetime.datetime.strptime(time_data, _format_from)
    except ValueError as ex:
        print(f"{datetime.datetime.now()} >> format_date_time -> ValueError >> {ex}")
        return ""
    except Exception as ex:
        print(f"{datetime.datetime.now()} >> format_date_time -> ExceptionError {ex}")
        return ""
    else:
        result_datetime = datetime.datetime.strftime(date_time, _format_to)
        return result_datetime


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


def has_special_char(text):
    pattern = r'[!@#$%^&*(),?":{}|<>]'
    if re.search(pattern, text):
        print(pattern)
        return True
    else:
        return False
