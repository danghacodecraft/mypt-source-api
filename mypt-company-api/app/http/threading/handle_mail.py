import threading
import base64
from django.template.loader import get_template
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers.utils import *
from ...core.helpers.mail import *
from django.conf import settings as project_settings

class HandleMail(threading.Thread):
    
    def __init__(self, subject, message, recipient_list, mail_data, reply=[""]):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.mail_data = mail_data
        self.reply = reply
        threading.Thread.__init__(self)
    
    def run(self):
        name = list(self.message.split("."))[0]
        print(f'handle email {name} running')
        if name == "improved_car":
            return self.improved_car()
        return self.base_mail_reply()
    
    def improved_car(self):
        print("improve car function send mail in")
        print(project_settings.APP_ENVIRONMENT)
        param1 = '{"actionType": "open_webkit","dataAction": "' + SERVICE_CONFIG["WEBKIT"][project_settings.APP_ENVIRONMENT]
        param2 = str(self.mail_data["id"]) + '"}'
        param = param1 + param2
        print(param)
        self.mail_data["deeplink"] = self.deeplink(param=param)
        list_img = self.mail_data["list_img"]
        sum_img = self.mail_data["len_img"]
        list_cid = []
        for i in range(1, sum_img+1):
            list_cid.append("img" + str(i))
        self.mail_data["cid_img"] = list_cid
        self.message = get_template(self.message).render(self.mail_data)
        data = {
            "recipient_list" : self.recipient_list,
            "subject" : self.subject,
            "message" : self.message,
            "reply" : self.reply,
            "list_img": self.mail_data
        }
        print("improve car function send mail out")
        return mail_improved_car(data=data)
    
    def deeplink(self, param):
        print('deeplink in')
        param = str(param)
        
        encoded = base64.b64encode(param.encode('ascii'))
        response = call_api_https(
            host = SERVICE_CONFIG['FCM_API_DEEPLINK']['base_http'],
            func = "",
            method = SERVICE_CONFIG['FCM_API_DEEPLINK']['method'],
            data = {
                "dynamicLinkInfo": {
                    "domainUriPrefix": "https://mypt.page.link",
                    "link": "https://mypt.page.link/" + encoded.decode('UTF-8'),
                    "androidInfo": {
                        "androidPackageName": "com.ftel.mypt"
                    }
                }
            }
        )
        self.param = json.loads(response)
        print('deeplink out')
        return self.param["shortLink"]

    def base_mail_param(self):
        self.message = get_template(self.message).render(self.mail_data)
        return send_email_fpt(subject=self.subject, message=self.message, recipient_list=self.recipient_list)
    
    def base_mail_reply(self):
        print('base_mail_reply in')
        param1 = '{"actionType": "open_webkit","dataAction": "'  + SERVICE_CONFIG["WEBKIT"][project_settings.APP_ENVIRONMENT]
        param2 = str(self.mail_data["idTree"]) + '"}'
        param = param1 + param2
        self.mail_data["deeplink"] = self.deeplink(param=param)
        self.message = get_template(self.message).render(self.mail_data)
        data = {
            "recipient_list" : self.recipient_list,
            "subject" : self.subject,
            "message" : self.message,
            "reply" : self.reply
        }
        print('base_mail_reply out')
        return mail_reply_improved_car(data=data)