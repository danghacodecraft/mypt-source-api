import threading
from ...configs.service_api_config import SERVICE_CONFIG
from core.helpers.utils import *
from django.conf import settings as project_settings
from ..entities import global_data
import json

class HandleShowHideTab(threading.Thread):
    
    def __init__(self, host={}, headers={}):
        self.host = host
        self.headers = headers
        self.hostSetting = SERVICE_CONFIG["SETTING"]["show_hide_tab"]
        threading.Thread.__init__(self)
        self.value = "None"
        
    def run(self):
        status_ptq = self.count_ptq()
        if status_ptq["statusCode"] != 1:
            return self.value
        for item in status_ptq["data"]:
            if status_ptq["data"][item] != 0:
                self.value = self.show_hide_tab()
                return self.value
        self.value = self.show_hide_tab(action_type="hide")
        return self.value
                
    def show_hide_tab(self, action_type="show", tab="cheTai"):
        data = {
            "userId": self.get_data_from_token(),
            "tabCode": tab,
            "actionType": action_type
        }
        app_env = project_settings.APP_ENVIRONMENT
        host = self.hostSetting[app_env]
        func = self.hostSetting["func"]
        method = self.hostSetting["method"]
        result = call_api(
            host=host,
            func=func,
            headers=self.headers,
            method=method,
            data=data
        )
        return json.loads(result)
        
    def get_data_from_token(self):
        try:
            logginedUserId = global_data.authUserSessionData.get("userId")
            return logginedUserId
        except:
            return None
    
    def count_ptq(self):
        app_env = project_settings.APP_ENVIRONMENT
        host = self.host[app_env]
        func = self.host["func"]
        method = self.host["method"]
        result = call_api(
            host=host,
            func=func,
            headers=self.headers,
            method=method,
            data={}
        )
       
        return json.loads(result)