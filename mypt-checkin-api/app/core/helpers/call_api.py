import requests
from .global_variables import  *
import json


def request_http(url, params=None, headers=None, get_request=False, auth=""):
    r = None
    try:
        # print(url)
        # print( ut.SELF_SIGNED_CERT_FILE2, os.path.isfile(ut.SELF_SIGNED_CERT_FILE2))
        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn",
        }
        if "https" in url:
            if not get_request:
                # r = requests.post(url=url, json=params, cert=(ut.CA_FILE, ut.KEY_FILE))
                r = requests.post(url=url, json=params, headers=headers, verify=False)
            else:
                # r = requests.get(url=url, json=params, verify=False)
                r = requests.get(url=url, verify=False, timeout=5)
        else:
            r = requests.post(url=url, json=params, headers=headers, auth=auth)
        print(r)
    except Exception as e:
        print("request_http >> {} ".format(e))
    return r

def call_api_noti_success_checkin(params):
    msg = "NOTOK"
    url = PRIVATE_HO_NOTIFICATION_URL + "mypt-ho-notification-api/" + "send-one-noti"
    try:

        # url = "https://apis-stag.fpt.vn/mypt-notification-api/v1/" + "send-noti"

        res = request_http(url=url, params=params)
        print(url)
        if res is not None:
            print("=========================check noti=======================")
            print(res.status_code)
            print(res.json())
            msg = "OK"
            print("call_api_noti_success_checkin {} - THANH CÔNG : res is  not none \n \n".format(url))
        else:
            print("call_api_noti_success_checkin >> {} >> THAT BAI : res is none ".format(url))
    except Exception as e:
        print("call_api_noti_success_checkin >> {} >> THAT BAI VI LOI: {} \n \n".format(url, e))
    return msg

def call_api_send_email(params):
    msg = "NOTOK"
    url = PRIVATE_HO_NOTIFICATION_URL + "mypt-ho-notification-api/" + "send-one-noti"
    try:

        # url = "https://apis-stag.fpt.vn/mypt-notification-api/v1/" + "send-noti"

        res = request_http(url=url, params=params)
        print(url)
        print("=====================BAN NOTI CALL API===================")
        if res is not None:
            print(res.status_code)
            msg = "OK"
            print("call_api_send_email {} - THANH CÔNG : res is none \n \n".format(url))
        else:
            print("call_api_send_email >> {} >> THAT BAI : res is none ".format(url))
    except Exception as e:
        print("call_api_noti_success_checkin >> {} >> THAT BAI VI LOI: {} \n \n".format(url, e))
    return msg


def call_api(**kwargs):
    try:
        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn",
        }
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        response = requests.request(method, host + func, headers=headers, data=payload, proxies=proxies)
        return response.text
    except:
        None


def hr_auth():
    payload = {
        "UserNameOrEmail": "pnc@hr.fpt.vn",
        "password": "!@#Pnc123"
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
    return dataApi['accessToken']


def get_employee_info(token="", email=""):
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


def call_api_change_shift(params):
    msg = "NOT OK"
    url = PRIVATE_HO_NOTIFICATION_URL + NAME_SERVICE_HO_NOTIFICATION + "send-multi-noti-with-diff-content-by-emp-code"
    try:

        # url = "https://apis-stag.fpt.vn/mypt-notification-api/v1/" + "send-noti"

        res = request_http(url=url, params=params['data'])
        if res is not None:
            # print(res.status_code)
            msg = "OK"
            print("call_api_noti_success_checkin {} - THANH CÔNG : res is NOT none \n \n".format(url))
        else:
            print("call_api_noti_success_checkin >> {} >> THAT BAI : res is none ".format(url))
    except Exception as e:
        print("call_api_noti_success_checkin {} >> THAT BAI VI LOI: {} \n \n".format(url, e))
    return msg

def call_api_disable_checkin(user_id, fname=""):
    msg = "NOT OK"
    url = PRIVATE_SETTING_URL + NAME_SERVICE_SETTING + "v1/update-shown-start-date-users-home-tabs"
    try:
        params = {
            "userId": user_id,
            "tabCode": "checkin"
        }

        # url = "https://apis-stag.fpt.vn/mypt-notification-api/v1/" + "send-noti"
        print(url)

        res = request_http(url=url, params=params)
        if res is not None:
            # print(res.status_code)
            print("================call_api_disable_checkin===================")
            msg = "OK"
            print("call_api_disable_checkin {} - THANH CÔNG : res is NOT none \n \n".format(url))
        else:
            print("call_api_disable_checkin >> {} >> THAT BAI : res is none ".format(url))
    except Exception as e:
        print("call_api_disable_checkin {} >> THAT BAI VI LOI: {} \n \n".format(url, e))
    return msg