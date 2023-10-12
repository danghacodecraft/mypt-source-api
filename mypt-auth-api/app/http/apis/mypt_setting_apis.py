import requests
import json
from app.configs import app_settings
from django.conf import settings as project_settings

class MyPtSettingApis:
    base_uri = ""

    def __init__(self):
        domainName = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "staging":
            # print("MyPtSettingApis : moi truong STAGING  - " + appEnv)
            domainName = app_settings.MYPT_SETTING_STAGING_DOMAIN_NAME
        elif appEnv == "production":
            # print("MyPtSettingApis : moi truong PRODUCTION - " + appEnv)
            domainName = app_settings.MYPT_SETTING_PRODUCTION_DOMAIN_NAME
        else:
            # print("MyPtSettingApis : moi truong LOCAL - " + appEnv)
            domainName = app_settings.MYPT_SETTING_LOCAL_DOMAIN_NAME

        self.base_uri = domainName + "/mypt-setting-api/" + app_settings.MYPT_SETTING_API_VER

    def assignDefaultTabsToUser(self, userId):
        apiUrl = self.base_uri + "/assign-default-tabs-to-user"
        inputParamsStr = json.dumps({
            "userId": int(userId)
        })
        headersDict = {
            "Content-Type": "application/json"
        }

        # print("URL mypt-setting-api assign tabs to user : " + apiUrl)
        # print("assign-default-tabs-to-user json input params : " + inputParamsStr)
        # print(headersDict)

        try:
            responseObj = requests.request("POST", apiUrl, headers=headersDict, data=inputParamsStr, timeout=5)
            print("Result call API mypt-setting-api assign tab to user : " + responseObj.text)
            responseData = json.loads(responseObj.text)
            # print(responseData)
            # return responseData

            if responseData.get("statusCode", None) is None:
                return None

            resData = None
            resCode = int(responseData.get("statusCode"))
            if resCode == 1:
                resData = responseData.get("data")

            return resData
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("Call mypt-setting from mypt-auth :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("Call mypt-setting from mypt-auth :Connection Timeout")

        return None