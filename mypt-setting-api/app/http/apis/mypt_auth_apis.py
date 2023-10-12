import requests
import json
from ...configs import app_settings
from django.conf import settings as project_settings

class MyPtAuthApis:
    base_uri = ""

    def __init__(self):
        domainName = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "staging":
            domainName = app_settings.MYPT_AUTH_STAGING_DOMAIN_NAME
        elif appEnv == "production":
            domainName = app_settings.MYPT_AUTH_PRODUCTION_DOMAIN_NAME
        else:
            domainName = app_settings.MYPT_AUTH_LOCAL_DOMAIN_NAME

        self.base_uri = domainName + "/mypt-auth-api/" + app_settings.MYPT_AUTH_API_VER

    def getOrCreateUserByEmail(self, email):
        apiUrl = self.base_uri + "/get-create-user-acc-by-email"
        inputParamsStr = json.dumps({
            "email": str(email)
        })
        headersDict = {
            "Content-Type": "application/json"
        }


        try:
            responseObj = requests.request("POST", apiUrl, headers=headersDict, data=inputParamsStr, timeout=5)
            responseData = json.loads(responseObj.text)
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
                print("Call API mypt-auth-api getOrCreateUserByEmail : Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("Call API mypt-auth-api getOrCreateUserByEmail : Connection Error")

        return None