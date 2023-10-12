import base64
import random
import re
import string
from datetime import datetime, timedelta

from Crypto.Util.Padding import pad
from Cryptodome.Cipher import AES

from .global_variables import *
from ..entities.centralized_session import CentralizedSession


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


def check_str_so_hop_dong(input_str, fname=""):
    # kiem tra xem chuoi nhap vao co 3 ky tu chu cai va 6 so hoac 4 ky tu chu cai va 5 so
    ok = False
    try:
        if not is_null_or_empty(input_str):
            txt = input_str.strip()
            txt = txt.lower()
            if re.findall("^[a-z]", txt):
                list_khoang_trang = re.findall("\s", txt)
                if len(list_khoang_trang) == 0:  # check xem co khoang trang hay ko
                    list_all_ky_tu = re.findall("\D", txt)
                    list_ky_tu_alpha = re.findall("[a-z]", txt)

                    if len(list_all_ky_tu) == len(list_ky_tu_alpha):
                        list_so = re.findall("\d", txt)
                        if len(list_all_ky_tu) == 3 and len(list_so) == 6:
                            ok = True
                        if len(list_all_ky_tu) == 4 and len(list_so) == 5:
                            ok = True
                        if len(list_all_ky_tu) == 5 and len(list_so) == 4:
                            ok = True
                        if len(list_all_ky_tu) == 6 and len(list_so) == 3:
                            ok = True
    except Exception as e:
        print("Error check_str_so_hop_dong {}: {}".format(fname, e))
    return ok


def is_none(v):
    if v is None:
        return True
    return False


def is_empty(_str):
    if isinstance(_str, str):
        return is_none(_str) or len(_str.strip()) == 0
    return False


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


def get_current_datetime():
    return datetime.utcnow() + timedelta(hours=7)


def get_str_datetime_now_import_db():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime(DATETIME_FORMAT)
    return str_time_now


def get_str_datetime_now_export_excel():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime(DATETIME_FORMAT_EXPORT_EXCEL)
    return str_time_now


def get_str_datetime_now():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime(DATETIME_FORMAT_EXPORT)
    return str_time_now


def get_str_date_now_import_db():
    str_time_now = get_str_datetime_now_import_db()
    str_date_now = str_time_now.split(" ")[0]
    return str_date_now


def convert_str_datetime_to_txt(str_time, fname=""):  # time = "%d/%m/%Y %H:%M:%S"
    t_create = ""
    try:
        # print(str_time)
        object_time = datetime.strptime(str_time, DATETIME_FORMAT_EXPORT)
        time_now = get_current_datetime()
        time_end = (time_now - object_time).total_seconds()
        time_end_minute = time_end / 60
        time_end_hours = time_end_minute / 60
        time_end_days = time_end_hours / 24
        if 0 < time_end_minute < 60:
            vi_tri = (str(time_end_minute)).find(".")
            t_create = (str(time_end_minute))[0:vi_tri] + " phút trước"
        elif 0 < time_end_hours < 24:
            vi_tri = (str(time_end_hours)).find(".")
            t_create = (str(time_end_hours))[0:vi_tri] + " giờ trước"
        elif 0 < time_end_days < 7:
            vi_tri = (str(time_end_days)).find(".")
            t_create = (str(time_end_days))[0:vi_tri] + " ngày trước"
        else:
            # t_create = str(ut.convert_dateDb(datetime.date(object_time)))
            t_create = object_time.strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        print("convert_str_datetime_to_txt >> Error get_time_comment {}: {}".format(fname, e))
    return t_create


def convert_str_datetime_to_datetime(str_datetime, fname=""):
    # str_datetime = DATETIME_FORMAT_EXPORT
    datetime_ouput = ""
    try:
        datetime_ouput_ = datetime.strptime(str_datetime, DATETIME_FORMAT_EXPORT)
        return datetime_ouput_
    except Exception as ex:
        print("convert_str_datetime_to_datetime >> Error/Loi: {}".format(fname, ex))
        return datetime_ouput


def convert_datetime_fr_DB_to_export(__datetime, fname=""):
    result = ""
    try:
        if __datetime is not None:
            result = datetime.strftime(__datetime, "%d/%m/%Y %H:%M:%S")
        else:
            result = str(__datetime)
    except Exception as e:
        print("{}: {}".format(fname, e))
    return result


def get_text_state_fr_sate_assiged_support(state, assigned, fname=""):
    if state == 0:
        if assigned is None:
            txt_state = "Chưa phân công"
        else:
            txt_state = "Đã phân công, chưa hỗ trợ"
    elif state == 1:
        txt_state = "Đang hỗ trợ"
    elif state == 2:
        txt_state = "Đã hỗ trợ hoàn tất"
    elif state == 3:
        txt_state = "Đã đánh giá"
    elif state == -1:
        txt_state = "Đang treo"
    else:
        txt_state = ""
    return txt_state


def date_time_to_minutes(datetime_object):
    return (
                datetime_object.day * 24 * 60) + datetime_object.hour * 60 + datetime_object.minute + datetime_object.second / 60


def to_list_fr_str(_str):
    if isinstance(_str, str):
        if len(_str) > 0:
            return _str.split(";")
    return []


def to_str_fr_list(_list):
    if isinstance(_list, list):
        return ';'.join([str(item) for item in _list])


def convert_str_to_datetime(str_datetime, fname=''):
    _datetime = None
    try:
        _datetime = datetime.strptime(str_datetime, DATETIME_FORMAT_EXPORT)
    except Exception as ex:
        print("convert_str_to_datetime >> {} >> Error/Loi: {}".format(fname, ex))
    return _datetime


def compute_interval(time_start, time_end, fname=""):
    try:
        dt = time_end - time_start
        _second = dt.seconds

        return _second
    except Exception as ex:
        print("compute_interval >> {} >> Error/Loi:{}".format(fname, ex))
        return None


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


def convert_datetime_to_str_date_export(_datetiem, fname):
    str_date = ""
    try:
        str_date = datetime.strftime(_datetiem, DATE_FORMAT_EXPORT)
    except Exception as ex:
        print("{} >> {} >> {} : Error/Loi: {}".format(get_str_datetime_now_import_db(),
                                                      "convert_datetime_to_str_date_export", fname, ex))
    return str_date
