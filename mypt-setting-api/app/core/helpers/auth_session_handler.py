from django.conf import settings as project_settings
# from . import global_variables
from ..entities.my_jwt import MyJwt
import redis
import ast

def getUserAuthSessionData(bearerAccessToken):
    if bearerAccessToken is None:
        return None

    bearerAccessToken = str(bearerAccessToken)
    if bearerAccessToken == "":
        return None

    accessTokenStr = bearerAccessToken.replace("Bearer ", "")
    if accessTokenStr == "":
        return None

    # Decode JWT auth token de lay duoc JTI
    jwtObj = MyJwt()
    payloadData = jwtObj.decodeJwtToken(accessTokenStr, False)
    if payloadData is None:
        return None

    if payloadData.get("jti", None) is None:
        return None

    jtiStr = payloadData.get("jti")

    sessionKey = "session:" + jtiStr

    centralRedisSer = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=project_settings.REDIS_DATABASE_CENTRALIZED
                                               , password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")

    sessionStr = centralRedisSer.get(sessionKey)
    if sessionStr is None:
        return None

    # convert string session nay thanh Dict
    sessionData = ast.literal_eval(sessionStr)
    # luu them JTI
    sessionData["accessTokenJti"] = jtiStr

    return sessionData

def getJtiFromAccessToken(bearerAccessToken):
    if bearerAccessToken is None:
        return ""

    bearerAccessToken = str(bearerAccessToken)
    if bearerAccessToken == "":
        return ""

    accessTokenStr = bearerAccessToken.replace("Bearer ", "")
    if accessTokenStr == "":
        return ""

    # Decode JWT auth token de lay duoc JTI
    jwtObj = MyJwt()
    payloadData = jwtObj.decodeJwtToken(accessTokenStr, False)
    if payloadData is None:
        return ""

    if payloadData.get("jti", None) is None:
        return ""

    jtiStr = payloadData.get("jti")
    return jtiStr
