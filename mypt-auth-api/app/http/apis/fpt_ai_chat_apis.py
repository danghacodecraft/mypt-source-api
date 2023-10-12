import requests
import json
from app.configs import app_settings
from django.conf import settings as project_settings

class FptAIChatApis:
    base_url = ""
    bot_token = ""
    app_env = "production"

    def __init__(self):
        self.base_url = "https://chatapi.fpt.ai"
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "production":
            self.bot_token = "0c87c397de6cec488ff6727ae9f1ed96"
        else:
            self.bot_token = "5ac7261033efcf2a118e32f88d89b38d"

        self.app_env = appEnv

    def createSenderToken(self, senderId):
        apiUrl = self.base_url + "/backend/chat-channel/live-chat/reset-access-token/" + senderId
        print("[FptAIChatApis] URL API ben FCI : " + apiUrl)

        try:
            proxies = {
                "http": None,
                "https": "proxy.hcm.fpt.vn",
            }

            headersData = {
                "Authorization": "Bearer " + self.bot_token
            }

            print("[FptAIChatApis] Headers API : ")
            print(headersData)

            apiResData = None
            if self.app_env == "staging" or self.app_env == "production":
                print("[FptAIChatApis] Can set proxy boi vi app env la : " + self.app_env)
                apiResData = requests.get(apiUrl,verify=True,
                                                      allow_redirects=False,
                                                      headers=headersData,
                                                      proxies=proxies,
                                                      timeout=3)
            else:
                print("[FptAIChatApis] Khong can set proxy boi vi app env la : " + self.app_env)
                apiResData = requests.get(apiUrl, verify=True,
                                          allow_redirects=False,
                                          headers=headersData,
                                          timeout=3)
            print("[FptAIChatApis] Ket qua API tao Sender Token : " + apiResData.text)

            try:
                tokenData = json.loads(apiResData.text)
            except Exception as token_ex:
                tokenData = None
            print(tokenData)
            if tokenData is None:
                return ""

            senderToken = tokenData.get("token", "")
            senderToken = str(senderToken).strip()
            print("[FptAIChatApis] Da tao duoc sender token: " + senderToken)
            return senderToken
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                print("[FptAIChatApis] Error call API tao Sender Token: Connection timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                print("[FptAIChatApis] Error call API tao Sender Token: Connection Error")

        return ""