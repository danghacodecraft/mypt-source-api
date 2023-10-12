import datetime
from ...configs.noti import *
from ...configs.service_api_config import *
from django.conf import settings as project_settings
import json
import requests
from django.db import close_old_connections


def device_token(**kwargs):
    try:
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        host = SERVICE_CONFIG["auth"][app_env]
        func = SERVICE_CONFIG["auth"]["get-user-device-info-by-email"]['func']
        method = SERVICE_CONFIG["auth"]["get-user-device-info-by-email"]['method']
        email = kwargs.pop("email", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(email)
        response = requests.request(method, host+func, headers=headers, data=payload)
        data_api = json.loads(response.text)
        if data_api["statusCode"] != 1:
            return ""
        data_api = data_api['data']['deviceToken']
        print(data_api)
        return data_api
    except:
        return ""
    
def send_noti(data={}):
    payload = notification_structure(data=data)
    print(payload)
    proxies = { 
        "http"  : "http://proxy.hcm.fpt.vn:80", 
        "https" : "http://proxy.hcm.fpt.vn:80"
    }
    
    if "registration_ids" in payload:
        payload.pop("registration_ids")
    if "actionButtons" in payload and payload["actionButtons"] is None:
        payload.pop("actionButtons")
    if "extraData" in payload and payload["extraData"] is None:
        payload.pop("extraData")
    headers = { 'Authorization': "Bearer " + SERVICE_CONFIG["fcm"]["server_key"] , 'Content-Type': 'application/json'}
    
    host = SERVICE_CONFIG["fcm"]["base_http"]
    func = SERVICE_CONFIG["fcm"]["sent"]
    method = SERVICE_CONFIG["fcm"]['method']
    response = requests.request(method, host+func, headers=headers, data=json.dumps(payload), proxies=proxies)
    # response = requests.request(method, host+func, headers=headers, data=json.dumps(payload))
    # print(response)
    return payload
    # return json.loads(response.text)

def notification_structure(data={}):
    structure = data
    structure["to"] = device_token(email={"email":data.pop("email","")})
    print(structure["to"])
    get_data(list_item=NOTI_HEAD, structure=structure)
    data_structure = get_data(list_item=NOTI_DATA, structure=structure)
    print(data_structure)
    return data_structure

def notification_structure_base(data={}):
    structure = data
    if "registration_ids" in structure or "to" in structure:
        structure.pop("registration_ids", None)
    structure["to"] = structure.pop("deviceToken", None)
    head = NOTI_HEAD.copy()
    body = NOTI_DATA.copy()
    get_data(list_item=head, structure=structure)
    data_structure = get_data(list_item=body, structure=structure)
    return data_structure

def get_data(data={}, list_item={}, structure={}):
    list_key = list_item.keys()
    for key in list_key:
        if isinstance(list_item[key], dict):
            data[key] = {}
            get_data(data[key], list_item[key], structure=structure)
        else:
            data[key] = structure.pop(key, list_item[key])
    return data
    
def send_structure_noti(noti=None, data={}):
    print(datetime.datetime.now())
    try:
        payload = data
        proxies = { 
            "http"  : "http://proxy.hcm.fpt.vn:80", 
            "https" : "http://proxy.hcm.fpt.vn:80"
        }
        headers = { 'Authorization': "Bearer " + SERVICE_CONFIG["fcm"]["server_key"] , 'Content-Type': 'application/json'}
        
        host = SERVICE_CONFIG["fcm"]["base_http"]
        func = SERVICE_CONFIG["fcm"]["sent"]
        method = SERVICE_CONFIG["fcm"]['method']
        # async with httpx.AsyncClient() as client:
        response = requests.request(method, host+func, headers=headers, data=payload, proxies=proxies)
        res_data_txt = response.text
        try:
            res_data = json.loads(res_data_txt)
            if noti:
                noti.is_send = res_data.get("success", 0)
        
        except Exception as e:
            print(e)
            
        if noti:
            noti.result_call_api = res_data_txt
            noti.save()

        close_old_connections()
        return
    except Exception as e:
        print("+++", e)
        return
    
def re_send_noti_send_failed(noti=None, data={}):
    try:
        device_info = get_user_device_info_by_email(noti.email)
        device_token = device_info.get("deviceToken", None)
        device_id = device_info.get("deviceId", None)
        data = json.loads(data)
        data['to'] = device_token
        data = json.dumps(data)
        
        if device_id is not None:
            noti.receive_device_id = device_id
        
        noti.data_input =  data
        # noti.save()
        return send_structure_noti(noti, data)

    except Exception as e:
        print("~~>", e, noti)
        return 
    
def get_user_device_info_by_email(email):
    try:
        domain = SERVICE_CONFIG["auth"][f"base_http_{project_settings.APP_ENVIRONMENT}"]
        func = SERVICE_CONFIG["auth"]["get-user-device-info-by-email"]['func']
        url = f"{domain}{func}"
        method = SERVICE_CONFIG["auth"]["get-user-device-info-by-email"]['method']
        payload = {
            "email": email
        }
        headers = {'Content-Type': 'application/json'}
        res = requests.request(method, url, data=json.dumps(payload), headers=headers)
        data = json.loads(res.text)
        return data['data']
    except Exception as e:
        print(e)
        return {}
    
def get_list_user_device_info_by_email(list_email):
        try:
            domain = SERVICE_CONFIG["auth"][f"base_http_{project_settings.APP_ENVIRONMENT}"]
            func = SERVICE_CONFIG["auth"]["get-user-devices-info-by-emails"]['func']
            url = f"{domain}{func}"
            method = SERVICE_CONFIG["auth"]["get-user-devices-info-by-emails"]['method']
            payload = {
                "emails": list_email
            }
            headers = {'Content-Type': 'application/json'}
            res = requests.request(method, url, data=json.dumps(payload), headers=headers)
            data = json.loads(res.text)
            data = data['data']
            if data:
                if "usersList" in data:
                    return data["usersList"]
                return []
            else:
                return []
        except Exception as e:
            print(e)
            return []  
    
    
