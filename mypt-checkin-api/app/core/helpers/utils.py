from Cryptodome.Cipher import AES
import time
import string
import random
import base64
from Crypto.Util.Padding import pad

from datetime import datetime, timedelta, date
import numpy as np
import math
from .global_variables import *
import json
import requests

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


def get_current_date():
    # return datetime.utcnow().date() + timedelta(hours=7)
    datetime_now = get_current_datetime()
    str_date_ = datetime.strftime(datetime_now, DATE_FORMAT)
    date_ = datetime.strptime(str_date_, DATE_FORMAT)
    return date_




def get_current_datetime():
    return datetime.utcnow() + timedelta(hours=7)

def calculate_distance_to(self, other):
    r = 6371  # Earth radius
    self = str(self)
    other = str(other)

    lat_dif = abs(float(self.split(",")[0]) - float(other.split(",")[0])) * math.pi / 180
    a = np.sin(lat_dif / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    lat_dis = r * c

    lon_dif = abs(float(self.split(",")[1]) - float(other.split(",")[1])) * math.pi / 180
    a = np.sin(lon_dif / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    lon_dis = r * c


    distance = abs(lat_dis) + abs(lon_dis)

    return distance

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

def calculate_workday_factor (branch, res_time, ca, location, fname="" ):
    time_in = datetime.strptime(res_time,'%Y-%m-%d %H:%M:%S')
    time_block = time_block_PNC()
    time_office = time_office_PNC()
    time_after_VP = time_after_VP_PNC()
    time_after_BL = time_after_BL_PNC()
    if branch == 'TIN':
        time_block = time_block_TIN()
        time_office = time_office_TIN()
        time_after_VP = time_after_VP_TIN()
        time_after_BL = time_after_BL_TIN()
    t_sang_BL= (time_in - time_block).total_seconds()
    t_sang_VP = (time_in - time_office).total_seconds()
    t_chieu_VP = (time_in - time_after_VP).total_seconds()
    t_chieu_BL = (time_in - time_after_BL).total_seconds()
    t_start_chieu = (time_in - time_start_chieu()).total_seconds()
    # tmp = 0
    if ca == 'S' and location == 'BLOCK':
        tmp = t_sang_BL
    elif ca == 'C' and location == 'VP' and t_start_chieu >= 0:
        tmp = t_chieu_VP
    elif ca == 'C' and location == 'BLOCK' and t_start_chieu >= 0 :
        tmp = t_chieu_BL
    else:
        tmp = t_sang_VP
    dict_workday = tinh_cong(tmp)
    data_workday = {
        "workday": dict_workday['ngay_cong'],
        "too_late": dict_workday['too_late']
    }
    return data_workday

def time_block_PNC():
    return get_current_datetime().replace(minute=00, hour=8, second=00, microsecond=0)

def time_office_PNC():
    return get_current_datetime().replace(minute=30, hour=7, second=00, microsecond=0)

def time_after_BL_PNC():
    return get_current_datetime().replace(minute=30, hour=13, second=00, microsecond=0)

def time_after_VP_PNC():
    return get_current_datetime().replace(minute=30, hour=13, second=00, microsecond=0)

def tinh_cong(t_second = 0.0, fname="" ):
    ngay_cong = 0
    too_late = 0
    if t_second <= 0:
        ngay_cong = 1
    elif t_second > 0 :
        if t_second / 28800 < 1:
            ngay_cong = round((1 - t_second / 28800), 2)
        else:
            too_late = 1

    dict_ngay_cong = {
        "ngay_cong": ngay_cong,
        "too_late": too_late
    }
    return dict_ngay_cong


def time_block_TIN():
    return get_current_datetime().replace(minute=30, hour=7, second=00, microsecond=0)


def time_office_TIN():
    return get_current_datetime().replace(minute=00, hour=7, second=00, microsecond=0)


def time_after_BL_TIN():
    return get_current_datetime().replace(minute=30, hour=14, second=00, microsecond=0)


def time_after_VP_TIN():
    return get_current_datetime().replace(minute=00, hour=14, second=00, microsecond=0)


def time_start_chieu():
    return get_current_datetime().replace(minute=00, hour=12, second=00, microsecond=0)


def calculate_distance_for_new_emp(coor_emp, toa_do_van_phong, toa_do_kho, toa_do_lam_viec, str_ban_kinh_lam_viec):
    print("-----------------------------CHECK COORDIATE NEW----------------------------")
    print(coor_emp)
    print(toa_do_lam_viec)
    print(toa_do_kho)
    print(toa_do_van_phong)
    print(str_ban_kinh_lam_viec)
    print("----------------------------------")
    try:
        ban_kinh_lam_viec = int(str_ban_kinh_lam_viec)

        if calculate_distance_to_for_new_emp(coor_emp, toa_do_van_phong) <= 200 or calculate_distance_to_for_new_emp(coor_emp , toa_do_kho) <= 200 :
            checkin = "OK"
            location = "VP"
        elif calculate_distance_to_for_new_emp(coor_emp, toa_do_lam_viec) <= ban_kinh_lam_viec :
            checkin = "OK"
            location = "BLOCK"
        else:
            checkin = "NOTOK"
            location = ""
        return {"checkin": checkin, "location": location}
    except Exception as ex:
        print("calculate_distance_for_new_emp----------------------------Error/Loi:{}".format(ex))
        return {"error": "ok"}

def calculcate_distance_for_official_emp(emp_coordinate, block_center, block_distance, office_center, block_name):

    print("-----------------------------CHECK COORDIATE----------------------------")
    print(emp_coordinate)
    print(block_center)
    print(office_center)
    print(block_distance)

    print("----------------------------------")
    try:
        if office_center.count(",") != 1 or office_center.count(".") != 2:
            coordinate_office = "0.0,0.0"
            distance_emp_to_office = calculate_distance_to_for_new_emp(emp_coordinate, coordinate_office)
        else:
            distance_emp_to_office = calculate_distance_to_for_new_emp(emp_coordinate, office_center)

        distance_emp_to_block = calculate_distance_to_for_new_emp(emp_coordinate, block_center)


        if distance_emp_to_block < block_distance and emp_coordinate != block_center:
            status_position = "OK"
            add_checkin = "BLOCK"
        elif distance_emp_to_office <= 200 and emp_coordinate != block_center:
            status_position = "OK"
            add_checkin = "VP"
        else:
            status_position = "NOTOK"
            add_checkin = ""

        return {"checkin": status_position, "location": add_checkin}
    except Exception as ex:
        print("calculcate_distance_for_official_emp >> Error/loi: {}".format(ex))
        return {"error": "ok"}


def calculate_distance_to_for_new_emp(self, other):
    r = 6371  # Earth radius

    lat_dif = abs(float(self.split(",")[0]) - float(other.split(",")[0])) * math.pi / 180
    a = np.sin(lat_dif / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    lat_dis = r * c


    lon_dif = abs(float(self.split(",")[1]) - float(other.split(",")[1])) * math.pi / 180
    a = np.sin(lon_dif / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    lon_dis = r * c


    distance = abs(lat_dis) + abs(lon_dis)
    return distance * 1000


def get_branch_fr_account_mobinet(emp_id):
    team_name = ""
    if not is_null_or_empty(emp_id):
        team_name = str(emp_id).split(".")[0]
    return team_name


def date_time_to_hour(datetime_object):
    return datetime_object.hour + datetime_object.minute / 60.0


def covert_date_vietnamese(time_now):
    thu = ""
    try:
        type_date = time_now.strftime("%A")

        if type_date == "Monday":
            thu = "Thứ 2, "
        elif type_date == "Tuesday":
            thu = "Thứ 3, "
        elif type_date == "Wednesday":
            thu = "Thứ 4, "
        elif type_date == "Thursday":
            thu = "Thứ 5, "
        elif type_date == "Friday":
            thu = "Thứ 6, "
        elif type_date == "Saturday":
            thu = "Thứ 7, "
        elif type_date == "Sunday":
            thu = "Chủ nhật, "

        str_time_now = time_now.strftime('%d/%m/%Y %H:%M:%S')
        full_day_init = str_time_now.split(" ")[0]
        full_day = full_day_init.split("/")

        __day = full_day[0]
        __month = full_day[1]
        __year = full_day[2]

        int_day = int(__day)
        int_month = int(__month)

        thu = thu + __day +"," + " Th" + str(int_month) + ", " + __year

    except Exception as e:
        print(e)

    return thu

def convert_date(time_now):
    thu = ""
    ngay = ""
    thang = ""
    full_day_init = ""
    try:
        type_date = time_now.strftime("%A")

        thu = convert_type_date_vietnamese(type_date)

        str_time_now = time_now.strftime('%d/%m/%Y %H:%M:%S')
        print(str_time_now)
        full_day_init = str_time_now.split(" ")[0]
        full_day = full_day_init.split("/")

        __day = full_day[0]
        __month = full_day[1]
        __year = full_day[2]

        ngay = int(__day)
        thang = convert_type_month_vietnames(__month)



    except Exception as e:
        print(e)

    return thu, ngay, thang, full_day_init

def convert_type_date_vietnamese(type_date):
    if type_date == "Monday":
        thu = "THỨ 2"
    elif type_date == "Tuesday":
        thu = "THỨ 3"
    elif type_date == "Wednesday":
        thu = "THỨ 4"
    elif type_date == "Thursday":
        thu = "THỨ 5"
    elif type_date == "Friday":
        thu = "THỨ 6"
    elif type_date == "Saturday":
        thu = "THỨ 7"
    elif type_date == "Sunday":
        thu = "CHỦ NHẬT"
    else:
        thu = ""
    return thu

def convert_type_month_vietnames(str_month):
    # str_month ="05"
    int_month = int(str_month)
    if int_month == 1:
        _month = "THÁNG 1"
    elif int_month == 2:
        _month = "THÁNG 2"
    elif int_month == 3:
        _month = "THÁNG 3"
    elif int_month == 4:
        _month = "THÁNG 4"
    elif int_month == 5:
        _month = "THÁNG 5"
    elif int_month == 6:
        _month = "THÁNG 6"
    elif int_month == 7:
        _month = "THÁNG 7"
    elif int_month == 8:
        _month = "THÁNG 8"
    elif int_month == 9:
        _month = "THÁNG 9"
    elif int_month == 10:
        _month = "THÁNG 10"
    elif int_month == 11:
        _month = "THÁNG 11"
    elif int_month == 12:
        _month = "THÁNG 12"
    else:
        _month = ""
    return _month

def get_full_str_shift(sheet_time):
    shift = ""
    if sheet_time == "S":
        shift = "Ca sáng"
    elif sheet_time == "C":
        shift = "Ca chiều"
    else:
        shift = "O"
    return shift

def compute_workday_for_offcial_workday(team_name, str_time_now, ca, location):
    status = 0
    check_in = "NOT OK"
    try:
        temp = datetime.strptime(str_time_now, '%Y-%m-%d %H:%M:%S')
        if ca == "S":
            time_block = get_current_datetime().replace(minute=00, hour=8, second=00, microsecond=0)
            time_office = get_current_datetime().replace(minute=30, hour=7, second=00, microsecond=0)
            if team_name in LIST_BLOCK:
                time_block = get_current_datetime().replace(minute=30, hour=7, second=00, microsecond=0)
                time_office = get_current_datetime().replace(minute=00, hour=7, second=00, microsecond=0)


            t_o_block = (temp - time_block).total_seconds()  # t sang block
            t_o_vp = (temp - time_office).total_seconds()  # t sang o van phong

            check_in = "OK"
            if location == "BLOCK":
                t_checkin = t_o_block
            else:
                t_checkin = t_o_vp

            if t_checkin <= 0:
                status = 1
            elif t_checkin / 28800 < 1:  # bo gia tri am (<0)
                status = round((1 - t_checkin / 28800), 2)
            else:
                status = 0
                check_in = "OK"
        else:
            time_evening_BL = get_current_datetime().replace(minute=30, hour=13, second=00,
                                                                               microsecond=0)
            t_checkin = (temp - time_evening_BL).total_seconds()

            check_in = "OK"

            if t_checkin <= 0:
                status = 1
            elif t_checkin / 28800 < 1:  # bo gia tri am (<0)
                status = round((1 - t_checkin / 28800), 2)
            else:
                status = 0
                check_in = "OK"

        workday_convert = status
        # if status < 0.7:
        #     workday_convert = 0

        dict_data = {
            "status": status,
            "check_in": check_in,
            "workday_convert": workday_convert
        }
        return dict_data

    except Exception as ex:
        print("compute_workday_for_offcial_workday >> {} ".format(ex))
        dict_data = {}
        return dict_data




def compute_workday_for_offcial_workday_old(team_name, str_time_now, ca):
    status = 0
    check_in = "NOT OK"
    try:
        time_block = get_current_datetime().replace(minute=00, hour=8, second=00, microsecond=0)
        time_office = get_current_datetime().replace(minute=30, hour=7, second=00, microsecond=0)
        time_evening_VP = time_evening_BL = get_current_datetime().replace(minute=30, hour=13, second=00,
                                                                       microsecond=0)
        time_start_chieu = get_current_datetime().replace(minute=00, hour=12, second=00, microsecond=0)
        if team_name in LIST_BLOCK:
            time_block = get_current_datetime().replace(minute=30, hour=7, second=00, microsecond=0)
            time_office = get_current_datetime().replace(minute=00, hour=7, second=00, microsecond=0)
            time_evening_BL = get_current_datetime().replace(minute=30, hour=13, second=00, microsecond=0)
            time_evening_VP = get_current_datetime().replace(minute=30, hour=13, second=00, microsecond=0)

        temp = datetime.strptime(str_time_now, '%Y-%m-%d %H:%M:%S')
        t1 = (temp - time_block).total_seconds()  # t sang block
        t = (temp - time_office).total_seconds()  # t sang o van phong

        t_chieu_VP = (temp - time_evening_VP).total_seconds()
        t_chieu_BL = (temp - time_evening_BL).total_seconds()
        # t3 = (temp - time_start_chieu).total_seconds() # rule cu
        t3 = (temp - time_evening_BL).total_seconds()

        # tinh ngay cong dua vao thoi diem checkin
        if ca == "C":
            if t3 >= 0:
                check_in = "OK"
                if t_chieu_BL <= 0:
                    status = 1
                elif t_chieu_BL > 0 and t_chieu_BL / 28800 < 1:
                    status = round((1 - t_chieu_BL / 28800), 2)
                else:
                    # qua tre
                    status = 0
                    check_in = "NOT OK"


            else:
                # qua som de diem danh
                check_in = "NOT OK"
                status = 0
        elif ca == "S":
            check_in = "OK"
            if t <= 0:
                status = 1
            elif t / 28800 < 1:  # bo gia tri am (<0)
                status = round((1 - t / 28800), 2)
            else:
                status = 0
                check_in = "NOT OK"
        else:
            status = 0
            check_in = "NOT OK"
            reason_failed = "CA OFF KHÔNG THỂ ĐIỂM DANH"
    except Exception as ex:
        print("compute_workday_for_offcial_workday >> {} ".format(ex))
    dict_data = {
        "status": status,
        "check_in": check_in
    }
    return dict_data


def get_str_datetime_now_import_db():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime(DATETIME_FORMAT)
    return str_time_now

def get_str_datetime_now_export():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime(DATETIME_FORMAT_EXPORT)
    return str_time_now


def get_str_date_now_import_db():
    str_time_now = get_str_datetime_now_import_db()
    str_date_now = str_time_now.split(" ")[0]
    return str_date_now

def get_str_date_now_export():
    str_time_now = get_str_datetime_now_import_db()
    str_date_now_ = str_time_now.split(" ")[0]
    str_date_now = datetime.strptime(str_date_now_, DATE_FORMAT_EXPORT_2).strftime(DATE_FORMAT_EXPORT)
    return str_date_now

# def get_str_datetime_now_export():
#     str_time_now = get_str_datetime_now_import_db()
#     # str_date_now_ = str_time_now.split(" ")[0]
#     str_date_now = datetime.strftime(str_time_now, DATETIME_FORMAT_EXPORT)
#     return str_date_now

def get_type_date_fr_str_date(str_date, fname):
    thu = ""
    try:
        _date = datetime.strptime(str_date, "%d/%m/%Y")
        type_date = _date.strftime("%A")
        thu = convert_type_date_vietnamese(type_date)

    except Exception as ex:
        print("get_type_date_fr_str_date >> {} >> Error/Loi: {}".format(fname, ex))

    return thu

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



def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn",
        }
        response = requests.request(method, host+func, headers=headers, data=payload, proxies=proxies)
        return response.text
    except:
        return None


def convert_str_to_date(str_date):
    # str_date = DATE_FORMAT_EXPORT
    _date = datetime.strptime(str_date, DATE_FORMAT_EXPORT)
    return _date

def convert_date_export(__date, fname=""):

    result = ""
    try:
        if __date is not None:
            result = datetime.strftime(__date, "%d/%m/%Y")
        else:
            result = str(__date)
    except Exception as e:
        print("{}: {}".format(fname, e))
    return result

def is_valid_date(_day, _month, _year):
    try:
        # newDate = datetime(2008,11,42)
        newDate = datetime(_year, _month, _day)
        correctDate = True
    except ValueError:
        correctDate = False
    return correctDate

def check_input_toa_do(toa_do):
    ok = True
    try:
        toa_do_1 = toa_do.split(",")
        if len(toa_do_1)== 2:
            lat = float(toa_do_1[0])
            long = float(toa_do_1[1])
    except Exception as ex:
        print("=========================check_input_toa_do====================================")
        print(ex)
        print(toa_do)
        ok = False
    return ok

def read_text_file_to_str(filename, fname=""):
    data = ''
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.read().replace('\n', '')
    except Exception as ex:
        print("====================read_text_file_to_str=====================")
        print("{}: {}".format(fname, ex))
    return data




