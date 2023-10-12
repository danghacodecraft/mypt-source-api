import requests
import json
from app.configs import app_settings
from django.conf import settings as project_settings

class MyPtProfileApis:
    base_uri = ""

    def __init__(self):
        domainName = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "staging":
            # print("MyPtProfileApis : moi truong staging")
            domainName = app_settings.MYPT_PROFILE_STAGING_DOMAIN_NAME
        elif appEnv == "production":
            # print("MyPtProfileApis : moi truong production")
            domainName = app_settings.MYPT_PROFILE_PRODUCTION_DOMAIN_NAME
        else:
            # print("MyPtProfileApis : moi truong local")
            domainName = app_settings.MYPT_PROFILE_LOCAL_DOMAIN_NAME

        self.base_uri = domainName + "/mypt-profile-api/" + app_settings.MYPT_PROFILE_API_VER

    def getProfileInfo(self, userId, email, fullName, extra = {}):
        apiUrl = self.base_uri + "/get-profile-info"
        inputParamsStr = json.dumps({
            "userId": int(userId),
            "email": email,
            "fullName": fullName,
            "specificChildDeparts": extra.get("specificChildDeparts", [])
        })
        headersDict = {
            "Content-Type": "application/json"
        }

        # print("URL mypt-profile-api get profile info : " + apiUrl)
        # print("get profile info json input params : " + inputParamsStr)

        try:
            # responseObj = requests.post(apiUrl, json=inputParams, timeout=5)
            responseObj = requests.request("POST", apiUrl, headers=headersDict, data=inputParamsStr, timeout=5)
            print("Result call API mypt-profile-api get profile info : " + responseObj.text)
            responseData = json.loads(responseObj.text)
            # print(responseData)
            # return responseData

            if responseData.get("statusCode", None) is None:
                return None

            infoData = None
            resCode = int(responseData.get("statusCode"))
            if resCode == 1:
                infoData = responseData.get("data")

            return infoData
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                print("call to mypt-profile-api :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                print("call to mypt-profile-api :Connection Timeout")

        return None


    def healthCheck(self):
        apiUrl = self.base_uri + "/health"

        print("URL mypt-profile-api health : " + apiUrl)

        try:
            responseObj = requests.request("GET", apiUrl, headers={}, timeout=5)
            print("Result call API mypt-profile-api health : " + responseObj.text)
            responseData = json.loads(responseObj.text)
            print(responseData)
            # return responseData

            if responseData.get("statusCode", None) is None:
                return None

            infoData = None
            resCode = int(responseData.get("statusCode"))
            if resCode == 1:
                infoData = responseData.get("data")

            return infoData
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("api_auth :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("api_auth :Connection Timeout")

        return None

    def getEmployeesInfoByEmails(self, emails=[]):
        apiUrl = self.base_uri + "/emps-info-by-emails"
        inputParamsStr = json.dumps({
            "emails": emails
        })
        headersDict = {
            "Content-Type": "application/json"
        }

        # print("URL mypt-profile-api get emps info by emails : " + apiUrl)
        # print("get emps info by emails json input params : " + inputParamsStr)

        try:
            responseObj = requests.request("POST", apiUrl, headers=headersDict, data=inputParamsStr, timeout=5)
            print("Result call API mypt-profile-api get emps info by emails : " + responseObj.text)
            responseData = json.loads(responseObj.text)
            if responseData.get("statusCode", None) is None:
                return []
            emps_info_data = []
            resCode = int(responseData.get("statusCode"))
            if resCode == 1:
                resData = responseData.get("data")
                emps_info_data = resData.get("emps_info_data")
            return emps_info_data
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                print("call to mypt-profile-api :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                print("call to mypt-profile-api :Connection Timeout")
        return []