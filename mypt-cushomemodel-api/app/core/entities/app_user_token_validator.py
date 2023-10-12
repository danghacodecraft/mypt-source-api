import ast
import json
from datetime import datetime

import redis
import rsa
from django.conf import settings as project_settings

from app.configs import app_settings
from app.core.helpers import utils as utHelper
from core.entities.my_rsa_alogrithm import MyRSA


class AppUserTokenValidator:
    redisInstance = None

    def __init__(self):
        self.redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")

    def validateAppUserTokenAndAppId(self, appUserToken, encryptedAppId):
        if self.redisInstance is None:
            return {
                "isValid": False,
                "errorMsg": "Redis connect failed"
            }

        # Decrypt encryptedAppId de lay ra appId
        appId = ""
        try:
            appId = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, encryptedAppId)
        except Exception as ex:
            appId = ""

        if appId == "":
            return {
                "isValid": False,
                "errorMsg": "App ID is invalid"
            }

        # check appId co hop le ko
        appsRsaKeysData = self.getAppsRsaKeysDataFromCache()
        if appsRsaKeysData is None:
            return {
                "isValid": False,
                "errorMsg": "No apps RSA Keys in cache"
            }

        availableAppIds = appsRsaKeysData["availableAppIds"]
        if appId not in availableAppIds:
            return {
                "isValid": False,
                "errorMsg": "App " + appId + " is not allowed"
            }

        # Check appId co trong appsRsaKeys ko. Co thi lay Private Key ra de chuan bi decrypt
        appsRsaKeys = appsRsaKeysData["appsRsaKeys"]
        appRsaKeyData = appsRsaKeys.get(appId, None)
        if appRsaKeyData is None:
            return {
                "isValid": False,
                "errorMsg": "Not found RSA keys of app " + appId
            }
        print("appId duoc chon : " + appId)
        # print(appRsaKeyData)
        privateKeyStr = appRsaKeyData.get("privateKey", "")
        private_key_obj = rsa.PrivateKey.load_pkcs1(privateKeyStr)

        my_rsa = MyRSA()
        appUserData_str = ""
        # decrypt appUserToken bang Private Key
        try:
            appUserData_str = my_rsa.decrypt(appUserToken, private_key_obj)
            print("Kieu du lieu cua appUserData_str : " + appUserData_str)
            print(type(appUserData_str))
        except Exception as ex:
            return {
                "isValid": False,
                "errorMsg": "Decrypt AppUserToken has been failed"
            }
        # convert appUserData_str qua Dict
        appUserData = None
        try:
            appUserData = json.loads(appUserData_str)
        except Exception as ex:
            appUserData = None

        if appUserData is None:
            return {
                "isValid": False,
                "errorMsg": "AppUserToken Data is not valid JSON"
            }

        print("Data of appUserData : ")
        print(appUserData)

        appIdInAppUserToken = appUserData.get("appId", None)
        if appIdInAppUserToken is None:
            return {
                "isValid": False,
                "errorMsg": "appId not found in AppUserToken Data"
            }

        if appIdInAppUserToken != appId:
            return {
                "isValid": False,
                "errorMsg": "app Id in AppUserToken Data is not matched with appId param : " + appIdInAppUserToken + " ; " + appId
            }

        # check accUsername tuong ung voi appId do co ton tai ko
        acc_username = ""
        if appIdInAppUserToken == "mobiqc":
            acc_username = str(appUserData.get("insideAcc", "")).strip()
            notExistMsg = "Inside Acc is not found with appId " + appIdInAppUserToken
        elif appIdInAppUserToken == "mobinet":
            acc_username = str(appUserData.get("mobinetAcc", "")).strip()
            notExistMsg = "Mobinet Acc is not found with appId " + appIdInAppUserToken
        elif appIdInAppUserToken == "mypt":
            acc_username = str(appUserData.get("email", "")).strip()
            notExistMsg = "Email is not found with appId " + appIdInAppUserToken
        else:
            acc_username = str(appUserData.get("saleclubAcc", "")).strip()
            notExistMsg = "Saleclub Acc is not found with appId " + appIdInAppUserToken

        if acc_username == "":
            return {
                "isValid": False,
                "errorMsg": notExistMsg
            }
        acc_username = acc_username.lower()

        return {
            "isValid": True,
            "appId": appIdInAppUserToken,
            "accUsername": acc_username,
            "fullName": str(appUserData.get("name", "")).strip()
        }

    def validateExToken(self, exToken):
        if self.redisInstance is None:
            return {
                "isValid": False,
                "errorMsg": "Redis connect failed"
            }

        # Decrypt exToken
        decryptedExToken = ""
        try:
            decryptedExToken = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, exToken)
        except Exception as ex:
            decryptedExToken = ""

        if decryptedExToken == "":
            return {
                "isValid": False,
                "errorMsg": "Decrypt exToken has been failed"
            }

        # convert decryptedExToken qua Dict
        exTokenData = None
        try:
            exTokenData = ast.literal_eval(decryptedExToken)
        except Exception as ex:
            exTokenData = None

        if exTokenData is None:
            return {
                "isValid": False,
                "errorMsg": "exToken Data is not valid JSON"
            }

        # check curDt pass ko
        curDtStr = exTokenData.get("curDt", "")
        if curDtStr == "":
            return {
                "isValid": False,
                "errorMsg": "Missing cur datetime info"
            }
        startDt = datetime.strptime(curDtStr, "%Y-%m-%d %H:%M:%S")
        startTs = int(startDt.timestamp())
        expiredTs = startTs + self.getAvailableTokenSeconds()
        curTs = int(datetime.now().timestamp())
        if curTs > expiredTs:
            return {
                "isValid": False,
                "errorMsg": "ExToken expired!",
                "curDtStr": curDtStr,
                "startTs": startTs,
                "avaiTokenSecs": self.getAvailableTokenSeconds(),
                "expiredTs": expiredTs,
                "curTs": curTs
            }

        # check appId & acc username pass ko
        appId = exTokenData.get("appId", "").lower()
        if appId == "":
            return {
                "isValid": False,
                "errorMsg": "App Id not found or empty"
            }
        # check appId hop le ko
        appsRsaKeysData = self.getAppsRsaKeysDataFromCache()
        if appsRsaKeysData is None:
            return {
                "isValid": False,
                "errorMsg": "No apps RSA Keys in cache"
            }
        availableAppIds = appsRsaKeysData["availableAppIds"]
        if appId not in availableAppIds:
            return {
                "isValid": False,
                "errorMsg": "App " + appId + " is not allowed"
            }

        # check accUsername tuong ung voi appId do co ton tai ko
        acc_username = ""
        if appId == "mobiqc":
            acc_username = str(exTokenData.get("insideAcc", "")).strip()
            notExistMsg = "Inside Acc is not found with appId " + appId
        elif appId == "mobinet":
            acc_username = str(exTokenData.get("mobinetAcc", "")).strip()
            notExistMsg = "Mobinet Acc is not found with appId " + appId
        elif appId == "mypt":
            acc_username = str(exTokenData.get("email", "")).strip()
            notExistMsg = "Email is not found with appId " + appId
        else:
            acc_username = str(exTokenData.get("saleclubAcc", "")).strip()
            notExistMsg = "Saleclub Acc is not found with appId " + appId

        if acc_username == "":
            return {
                "isValid": False,
                "errorMsg": notExistMsg
            }
        acc_username = acc_username.lower()

        return {
            "isValid": True,
            "appId": appId,
            "accUsername": acc_username
        }

    def validateSessionToken(self, sessionToken):
        if self.redisInstance is None:
            return {
                "isValid": False,
                "errorMsg": "Redis connect failed"
            }

        # Decrypt sessionToken
        decryptedSessionToken = ""
        try:
            decryptedSessionToken = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, sessionToken)
        except Exception as ex:
            decryptedSessionToken = ""

        if decryptedSessionToken == "":
            return {
                "isValid": False,
                "errorMsg": "Decrypt sessionToken has been failed"
            }

        # convert decryptedSessionToken qua Dict
        sessionTokenData = None
        try:
            sessionTokenData = ast.literal_eval(decryptedSessionToken)
        except Exception as ex:
            sessionTokenData = None

        if sessionTokenData is None:
            return {
                "isValid": False,
                "errorMsg": "sessionToken Data is not valid JSON"
            }

        print("Data sessionToken sau khi convert qua Dict :")
        print(sessionTokenData)

        # check startTs pass ko
        startTs = 0
        try:
            startTs = int(sessionTokenData.get("startTs", 0))
        except Exception as ex:
            startTs = 0

        if startTs <= 0:
            return {
                "isValid": False,
                "errorMsg": "Missing Start TS info"
            }

        expiredTs = startTs + self.getAvailableTokenSeconds()
        curTs = int(datetime.now().timestamp())
        if curTs > expiredTs:
            return {
                "isValid": False,
                "errorMsg": "SessionToken expired!",
                "startTs": startTs,
                "avaiTokenSecs": self.getAvailableTokenSeconds(),
                "expiredTs": expiredTs,
                "curTs": curTs
            }

        print("startTs hop le :")
        print("startTs : " + str(startTs) + " ; avaiTokenSecs : " + str(
            self.getAvailableTokenSeconds()) + " ; expiredTs : " + str(expiredTs) + " ; curTs : " + str(curTs))

        # check appId & acc username pass ko
        appId = sessionTokenData.get("appId", "").lower()
        if appId == "":
            return {
                "isValid": False,
                "errorMsg": "App Id not found or empty"
            }
        # check appId hop le ko
        appsRsaKeysData = self.getAppsRsaKeysDataFromCache()
        if appsRsaKeysData is None:
            return {
                "isValid": False,
                "errorMsg": "No apps RSA Keys in cache"
            }
        availableAppIds = appsRsaKeysData["availableAppIds"]
        if appId not in availableAppIds:
            return {
                "isValid": False,
                "errorMsg": "App " + appId + " is not allowed"
            }

        # check accUsername tuong ung voi appId do co ton tai ko
        acc_username = ""
        if appId == "mobiqc":
            acc_username = str(sessionTokenData.get("insideAcc", "")).strip()
            notExistMsg = "Inside Acc is not found with appId " + appId
        elif appId == "mobinet":
            acc_username = str(sessionTokenData.get("mobinetAcc", "")).strip()
            notExistMsg = "Mobinet Acc is not found with appId " + appId
        elif appId == "mypt":
            acc_username = str(sessionTokenData.get("email", "")).strip()
            notExistMsg = "Email is not found with appId " + appId
        else:
            acc_username = str(sessionTokenData.get("saleclubAcc", "")).strip()
            notExistMsg = "Saleclub Acc is not found with appId " + appId

        if acc_username == "":
            return {
                "isValid": False,
                "errorMsg": notExistMsg
            }
        acc_username = acc_username.lower()

        return {
            "isValid": True,
            "appId": appId,
            "accUsername": acc_username
        }

    def getAvailableTokenSeconds(self):
        app_env = project_settings.APP_ENVIRONMENT
        if app_env == "local":
            return app_settings.LOCAL_AVAILABLE_TOKEN_SECONDS
        elif app_env == "staging":
            return app_settings.STAGING_AVAILABLE_TOKEN_SECONDS
        else:
            return app_settings.PRODUCTION_AVAILABLE_TOKEN_SECONDS

    def getAccountUsernameKeyByAppId(self, appId):
        if appId == "mobiqc":
            accUsernameKey = "insideAcc"
        elif appId == "mobinet":
            accUsernameKey = "mobinetAcc"
        elif appId == "mypt":
            accUsernameKey = "email"
        else:
            accUsernameKey = "saleclubAcc"
        return accUsernameKey

    # Ham nay tra ve cac cap Public Key - Private Key cua cac app tu Redis, va cac app Id
    def getAppsRsaKeysDataFromCache(self):
        appsRsaKeysStr = self.redisInstance.get("appsRSAKeys")
        if appsRsaKeysStr is None:
            return None

        appsRsaKeys = None
        try:
            appsRsaKeys = ast.literal_eval(appsRsaKeysStr)
        except Exception as ex:
            appsRsaKeys = None
        if appsRsaKeys is None:
            return None

        appIds = list(appsRsaKeys.keys())
        return {
            "appsRsaKeys": appsRsaKeys,
            "availableAppIds": appIds
        }
