import requests
# import pycurl
# import certifi
# from io import BytesIO
from decouple import config
from django.conf import settings as project_settings
import json
from ...configs.service_api_config import *

from app.core.helpers.response import response_data

class FCMApi:        
    def sent_notification(data):            
        try:            
            # serverKey = "AAAANEsF02U:APA91bE1NBt9Hs94C2BZZq5DsSq2FDPDCCmWiG5Bml1bZ9Z6zm4qVrzBVQz8H2T7QSzpHO7Ts5SZ_dyNVmMmPt8cGDZ2qYnQUJ0F7M9wVSgFLcy8nyrZ7thHamOZqB0rdpbLFOjI8KUh"
            serverKey = 'AAAAt8aIEiQ:APA91bEIqBfqTHI0-0xavXrh0U7CJguWaQXZ1CTBmpNHgEkI6ciV7QrRTlzyckRhDkM9lMw2RDfqdc7rkGHD6pMxl5z9IZ4nOE_n6AtNkyNPRlEgRImZ1ipMPZekmX26TWAbf3WYxLOM'
            url = "https://fcm.googleapis.com/fcm/send"
            headers = { 'Authorization': "key=" + serverKey }
            
            res = requests.post(url=url, json=data, headers=headers, proxies=project_settings.PROXIES)
            return res.json()
            # res.status_code
        except Exception as e:
            return format(e)

    def test_call_url_pr():
        try:
            url = project_settings.PROFILE_SERVICE + "/v1/health"
            print(url)
            res = requests.get(url=url, proxies=project_settings.PROXIES)
            return res.json()
            # res.status_code
        except Exception as e:
            return format(e)

    def test_call_url_pr_noproxy():
        url = project_settings.PROFILE_SERVICE + "/v1/health"
        try:
            if(project_settings.APP_ENV == 'local'):
                res = requests.get(url=url, proxies=project_settings.PROXIES)
            
            res = requests.get(url=url)
            print(url)            
            return res.json()
            # res.status_code
        except Exception as e:
            return format(e)
