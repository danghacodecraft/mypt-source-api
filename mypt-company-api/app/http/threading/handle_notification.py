import threading
import base64
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers.utils import *
from ...core.helpers.mail import *
from django.conf import settings as project_settings

class HandleNotification(threading.Thread):
    
    def __init__(self, data={}):
        self.data = data
        threading.Thread.__init__(self)
        
    def run(self):
        return self.call_notification()
        
    def call_notification(self):
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        result = call_api(
            host=SERVICE_CONFIG["NOTIFICATION"][app_env],
            func=SERVICE_CONFIG["NOTIFICATION"]["send_noti"]["func"],
            method=SERVICE_CONFIG["NOTIFICATION"]["send_noti"]["method"],
            data=self.data
        )
        print(result)
        return result