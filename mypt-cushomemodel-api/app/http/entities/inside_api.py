import json

import requests
from django.conf import settings as project_settings

from app.configs.service_api_config import INSIDE_CONFIG
from app.core.helpers import utils


def get_list_equipment():
    result = None
    base_env = project_settings.APP_ENVIRONMENT
    payload = 'UserName=sp-new-wc-inside&PassWord=!@#Admin@123'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    url = INSIDE_CONFIG['LIST_EQUIPMENTS_INFO'][base_env] + INSIDE_CONFIG['LIST_EQUIPMENTS_INFO']['authenticate'][
        'func']
    method = INSIDE_CONFIG['LIST_EQUIPMENTS_INFO']['authenticate']['method']
    response = requests.request(method, url, headers=headers, data=payload).text
    response_json = json.loads(response)
    if response_json['Succeeded']:
        headers = {
            'Authorization': 'Bearer ' + response_json['Data']['JwtToken']
        }
        response = utils.call_api(
            host=INSIDE_CONFIG['LIST_EQUIPMENTS_INFO'][base_env],
            func=INSIDE_CONFIG['LIST_EQUIPMENTS_INFO']['get_list_equipment_info']['func'],
            method=INSIDE_CONFIG['LIST_EQUIPMENTS_INFO']['get_list_equipment_info']['method'],
            headers=headers,
        )
        result = list(map(lambda data: {
            'name': data['ParentName'],
            'codeID': data['CodeID'],
            'LANWifi': data['LANWifi'],
            'wifi': data['Wifi'],
            'modemRule': data['ModemRule'],
            'quantityWAN': data['QuantityWAN'],
            'wifi24Pow': None,
            'wifi5Pow': None
        }, json.loads(response)['Data']))

    return result
