from datetime import datetime
from datetime import timedelta
from django.conf import settings as project_settings
from app.core.entities.my_jwt import MyJwt
import redis
import ast
import re

class CentralizedSession:
    redisInstance = None
    sessionPrefix = "session:"

    def __init__(self):
        self.redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
            , port=project_settings.REDIS_PORT_CENTRALIZED
            , db=project_settings.REDIS_DATABASE_CENTRALIZED, password=project_settings.REDIS_PASSWORD_CENTRALIZED
            , decode_responses=True, charset="utf-8")

    def saveSession(self, sessionKey, sessionData, seconds):
        if self.redisInstance is None:
            return {
                "resSave": False
            }

        finalSessionKey = self.sessionPrefix + sessionKey
        resSave = self.redisInstance.set(finalSessionKey, str(sessionData), seconds)
        if resSave == True:
            return {
                "resSave": True
            }
        else:
            return {
                "resSave": False
            }

    def removeSession(self, sessionKey):
        finalSessionKey = self.sessionPrefix + sessionKey
        self.redisInstance.delete(finalSessionKey)
        return {
            "resRemove": True
        }

    def validateSession(self, accessToken):
        result = {
            "errorCode": "access_token_failed",
            "errorMsg": "Access token failed",
            "sessionData": None
        }

        # validate JWT auth token xem hop le ko
        # print(accessToken)
        # jwtParts = accessToken.split(".")
        # if isinstance(jwtParts, (list)) == False or len(jwtParts) != 3:
        #     print("len cua jwt parts day : " + str(len(jwtParts)))
        #     result["errorMsg"] = "AccessToken format is not valid"
        #     return result
        # print("len cua jwt parts : " + str(len(jwtParts)))

        regexPat = "^[A-Za-z0-9-_+=]+\.[A-Za-z0-9-_+=]+\.[A-Za-z0-9-_+=]+$"
        matchedList = re.findall(regexPat, accessToken)
        # print(matchedList)
        if len(matchedList) == 0:
            result["errorMsg"] = "Access Token format is invalid"
            return result

        # Decode JWT auth token de lay duoc JTI
        jwtObj = MyJwt()
        payloadData = jwtObj.decodeJwtToken(accessToken, True)
        if payloadData is None:
            result["errorMsg"] = "AccessToken is invalid"
            return result

        if payloadData.get("jti", None) is None:
            result["errorMsg"] = "AccessToken is not defined correctly"
            return result

        jtiStr = payloadData.get("jti")
        # print("ta co duoc JTI : " + jtiStr)

        # tim trong Redis co JTI nay hay ko
        sessionData = self.getSession(jtiStr)
        if sessionData is None:
            result["errorCode"] = "redis_session_expired"
            result["errorMsg"] = "Session expired"
            return result

        result["errorCode"] = "no_error"
        result["errorMsg"] = "No error"
        result["sessionData"] = sessionData
        return result

    def getSession(self, sessionKey):
        finalSessionKey = self.sessionPrefix + sessionKey
        sessionStr = self.redisInstance.get(finalSessionKey)
        if sessionStr is None:
            return None

        # convert string session nay thanh Dict
        sessionData = ast.literal_eval(sessionStr)

        return sessionData