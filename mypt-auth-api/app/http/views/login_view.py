from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ...myCore.helpers.response import *
from django.shortcuts import redirect
import jwt
import base64
import json
from datetime import datetime
from django.conf import settings as project_settings
from app.configs import app_settings
from app.myCore.helpers import utils as utHelper
from app.myHttp.Entities import global_data
from app.myHttp.Apis.fpt_adfs_apis import FptAdfsApis
from app.myHttp.Entities.oauth_client_grants_handler import OauthClientGrantsHandler
from app.myHttp.Entities.authen_handler import AuthenHandler
import redis
import time
from app.myHttp.Apis.mypt_profile_apis import MyPtProfileApis
from ..apis.microsoft_azure_apis import MicrosoftAzureApis
from app.myCore.Entities.my_jwt import MyJwt
from ...myCore.helpers import auth_session_handler as authSessionHandler

# import uuid
# from app.myHttp.models.so_vong_quay import SoVongQuay
# from app.myHttp.models.lich_su_quay_so import LichSuQuaySo
# from app.myHttp.serializers.sovongquay_serializer import SoVongQuaySerializer

# Create your views here.
@api_view(["GET"])
def showLogin(request):
    protocol = "http://"
    domainName = request.get_host()
    if domainName == "apis-stag.fpt.vn" or domainName == "apis.fpt.vn":
        protocol = "https://"

    redirectUri = protocol + domainName + "/" + app_settings.ROUTES_PREFIX + "adfs-token"

    authorization_redirect_url = "https://adfs.fpt.com.vn/adfs/oauth2/authorize/?response_type=code&client_id=MyTin-PNC&redirect_uri=" + redirectUri + "&scope=openid%20email%20profile"
    return redirect(authorization_redirect_url)


@api_view(["GET"])
def showAzureLogin(request):
    redirectUriAfterSuccess = ""
    appEnv = str(project_settings.APP_ENVIRONMENT)
    if appEnv == "staging":
        print("day la env staging : " + appEnv)
        redirectUriAfterSuccess = "https://apis-stag.fpt.vn/mypt-auth-api/v1/azure-token"
    elif appEnv == "production":
        print("day la env production : " + appEnv)
        redirectUriAfterSuccess = "https://apis.fpt.vn/mypt-auth-api/v1/azure-token"
    else:
        print("day la env local : " + appEnv)
        redirectUriAfterSuccess = "http://localhost:4200"

    print("redirect URI cho Azure : " + redirectUriAfterSuccess)

    redirect_url = "https://login.microsoftonline.com/4ebc9261-871a-44c5-93a5-60eb590917cd/oauth2/authorize?client_id=" + app_settings.AZURE_CLIENT_ID + "&response_type=code&response_mode=query&redirect_uri=" + redirectUriAfterSuccess

    print("URL Azure chuan bi redirect : " + redirect_url)

    return redirect(redirect_url)

@api_view(["GET"])
def getAdfsToken(request):
    # lay param code
    adfsCode = request.GET.get("code")
    if adfsCode is None:
        return Response({"errorMsg": "missing code"}, status.HTTP_200_OK)

    adfsCode = str(adfsCode)
    if adfsCode == "":
        return Response({"errorMsg": "code is empty"}, status.HTTP_200_OK)
    # return Response({"adfsCode": adfsCode}, status.HTTP_200_OK)

    fptAdfsObj = FptAdfsApis()
    # set callBackUri
    protocol = "http://"
    domainName = request.get_host()
    if domainName == "apis-stag.fpt.vn" or domainName == "apis.fpt.vn":
        protocol = "https://"

    callBackUri = protocol + domainName + "/" + app_settings.ROUTES_PREFIX + "adfs-token"

    adfsToken = fptAdfsObj.get_adfs_token(adfsCode, callBackUri)
    if adfsToken == "":
        return Response({"errorMsg": "get token failed"}, status.HTTP_200_OK)

    # adfsToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjlETHhGbDhMYVh5cklVX1VMdWM0bHh4aXpCMCIsImtpZCI6IjlETHhGbDhMYVh5cklVX1VMdWM0bHh4aXpCMCJ9.eyJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjQyMDAiLCJpc3MiOiJodHRwOi8vYWRmcy5mcHQuY29tLnZuL2FkZnMvc2VydmljZXMvdHJ1c3QiLCJpYXQiOjE2NDg2OTQxODIsIm5iZiI6MTY0ODY5NDE4MiwiZXhwIjoxNjQ4Njk3NzgyLCJ1cG4iOlsicG5jLlBEWEBmcHQubmV0IiwicG5jLnBkeEBmcHQubmV0Il0sImVtYWlsIjoicG5jLlBEWEBmcHQubmV0IiwidW5pcXVlX25hbWUiOlsiUGhvbmcgUERYIiwiRlRFTFxccG5jLlBEWCJdLCJhcHB0eXBlIjoiQ29uZmlkZW50aWFsIiwiYXBwaWQiOiJNeVRpbi1QTkMiLCJhdXRobWV0aG9kIjoidXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFjOmNsYXNzZXM6UGFzc3dvcmRQcm90ZWN0ZWRUcmFuc3BvcnQiLCJhdXRoX3RpbWUiOiIyMDIyLTAzLTMxVDAyOjM2OjIyLjU3MFoiLCJ2ZXIiOiIxLjAiLCJzY3AiOiJvcGVuaWQifQ.aHY88H6ppbp6hf-ZSY_I5sLFyUTsXgKERaMWIIIJwXK_QqSbDlpP2Cld0TBpJIAv5f3fciXm7ZPbOpcDPgz_UMT4uaMFuOJ6fihdxaF9aqcfNzWPDp7LMrPA09nWbU38cmuoQspOb5xO8RAYlE-jPv57S15SfJqsqKrw0EzLZ0thm2m2y4F7FK58BQXTyhkvZw4DgOl7y5sW-BHug_9AKOgGvMN6PgFIZgsvrBzlX7DI40SVP70WIggjDkKi7nLVP1mrEpmga9F3qH9LO1CV_wmJDklFcVSny0AyiF2PGPJ6sPHTaFm1SM7zDCNZKVcYRsU6HAadYhLS6BZq4PAEHg"
    adfsTokenParts = adfsToken.split(".")
    if len(adfsTokenParts) != 3:
        return Response({}, status.HTTP_404_NOT_FOUND)

    # them == vao cuoi string thi moi decode base64 duoc
    encodedStr = adfsTokenParts[1] + "=="
    loginUserInfoStr = base64.b64decode(encodedStr)
    loginUserInfo = json.loads(loginUserInfoStr)
    print(loginUserInfo)
    userEmail = loginUserInfo.get("email")
    userFullNames = loginUserInfo.get("unique_name")

    userInfoDic = {
        "email": userEmail,
        "name": userFullNames[0]
    }
    encodedUserInfoStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(userInfoDic))

    curTs = int(datetime.now().timestamp())
    print("cur timestamp : " + str(curTs))
    exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(curTs))

    redirectUrl = protocol + domainName + "/" + app_settings.ROUTES_PREFIX + "do-auth?token=" + encodedUserInfoStr + "&extoken=" + exToken + "&isAuthed=1"
    return redirect(redirectUrl)

    # return Response({"userEmail": userEmail, "userFullName": userFullNames[0]}, status.HTTP_200_OK)

@api_view(["GET"])
def getAzureToken(request):
    # lay param code
    azureCode = request.GET.get("code")
    if azureCode is None:
        return response_data(None, 5, "missing AZURE code")

    azureCode = str(azureCode)
    if azureCode == "":
        return response_data(None, 5, "AZURE code is empty")

    # goi API ben Azure de lay Token tu Azure Code
    azureObj = MicrosoftAzureApis()
    # dua theo APP_ENV de chon ra callBackUri
    callBackUri = ""
    appEnv = str(project_settings.APP_ENVIRONMENT)
    if appEnv == "production":
        callBackUri = "https://apis.fpt.vn/mypt-auth-api/v1/azure-token"
    elif appEnv == "staging":
        callBackUri = "https://apis-stag.fpt.vn/mypt-auth-api/v1/azure-token"
    else:
        callBackUri = "http://localhost:4200"
    # call API ben Azure
    azureObj.app_env = appEnv
    azureToken = azureObj.getAzureToken(azureCode, callBackUri)
    print("[getAzureToken] AZURE Token tra ve tu API la : " + azureToken)
    if azureToken == "":
        return response_data(None, 6, "Get Azure Token by code has been failed")

    # dung jwt decode Azure Token
    jwtObj = MyJwt()
    jwtObj.jwtAlgorithm = "RS256"
    azureTokenData = jwtObj.decodeJwtToken(azureToken, False)
    if azureTokenData is None:
        return response_data(None, 6, "Get Azure Token by code failed")

    print("[getAzureToken] Azure Token Data sau khi decode jwt :")
    print(azureTokenData)
    userEmail = azureTokenData.get("preferred_username", "")
    if userEmail == "":
        return response_data(None, 6, "Get Azure Token by code failed because of missing email")
    userEmail = userEmail.lower()
    fullName = azureTokenData.get("name", "")

    userInfoDic = {
        "email": userEmail,
        "name": fullName
    }
    print(userInfoDic)
    encodedUserInfoStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(userInfoDic))

    curTs = int(datetime.now().timestamp())
    print("[getAzureToken] Azure cur timestamp : " + str(curTs))
    exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(curTs))

    protocol = "http://"
    if appEnv == "staging" or appEnv == "production":
        protocol = "https://"
    domainName = request.get_host()

    redirectUrl = protocol + domainName + "/" + app_settings.ROUTES_PREFIX + "do-auth?token=" + encodedUserInfoStr + "&extoken=" + exToken + "&isAuthed=1"
    return redirect(redirectUrl)

@api_view(["GET"])
def doAuth(request):
    return Response({}, status.HTTP_200_OK)

# Muon tam API logout de test Chat bot
@api_view(["POST"])
def doLogout(request):
    redirectUriAfterLogoutAzure = ""
    appEnv = str(project_settings.APP_ENVIRONMENT)
    if appEnv == "production":
        redirectUriAfterLogoutAzure = "https://apis.fpt.vn/mypt-auth-api/v1/azure-token"
    elif appEnv == "staging":
        redirectUriAfterLogoutAzure = "https://apis-stag.fpt.vn/mypt-auth-api/v1/azure-token"
    else:
        redirectUriAfterLogoutAzure = "http://localhost:4200"

    azureLogoutUrl = "https://login.microsoftonline.com/fptcloud.onmicrosoft.com/oauth2/v2.0/logout?post_logout_redirect_uri=" + redirectUriAfterLogoutAzure

    authenJti = ""
    # Lay authen session trong Redis tu Access Token
    authSessionData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
    if authSessionData is None:
        # lay ra JTI tu Access Token
        authenJti = authSessionHandler.getJtiFromAccessToken(request.headers.get("Authorization"))
        if authenJti == "":
            return Response({
                "statusCode": 1,
                "message": "SUCCESS",
                "data": {
                    "resLogout": {"result": True},
                    "azureLogoutUrl": azureLogoutUrl
                }
            }, status.HTTP_200_OK)
    else:
        authenJti = authSessionData["accessTokenJti"]

    authHandler = AuthenHandler()
    resLogout = authHandler.doLogout(authenJti)
    if resLogout.get("result") == True:
        resData = {
            "statusCode": 1,
            "message": "SUCCESS",
            "data": {
                "resLogout": resLogout,
                "azureLogoutUrl": azureLogoutUrl
            }
        }
    else:
        resData = {
            "statusCode": 6,
            "message": "Error",
            "data": {
                "resLogout": resLogout
            }
        }

    return Response(resData, status.HTTP_200_OK)

@api_view(["GET"])
def healthCheck(request):
    # test lay domain name tu request
    domainName = request.get_host()

    # test ket noi mysql db
    ocgHandler = OauthClientGrantsHandler()
    clientGrantInfo = ocgHandler.findByGrantIdAndClientId(9, app_settings.OAUTH_CLIENT_ID)

    # test ket noi redis
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                           , port=project_settings.REDIS_PORT_CENTRALIZED
                                           , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                           , decode_responses=True, charset="utf-8")

    resSetRedisKey = redisInstance.set("myptauthPhong", "Day la value cua Redis key myptauthPhong SIEU NHAN SUPERMAN SPIDER MAN", 3600)
    print("redis value cua myptauth : " + redisInstance.get("myptauthPhong"))

    print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
    print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
    print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

    resData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "clientGrantInfo": clientGrantInfo,
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "testRedisVal": redisInstance.get("myptauthPhong"),
            "domainName": domainName,
            "appEnv": project_settings.APP_ENVIRONMENT
        }
    }

    return Response(resData, status.HTTP_200_OK)

# API nay de tao ra doan encode User Info de truyen vao API /user-token de tao Access Token
@api_view(["POST"])
def genLogginedUserToken(request):
    postData = request.data
    email = postData.get("email")
    fullName = postData.get("fullName")

    userInfoDic = {
        "email": email,
        "name": fullName
    }
    encodedUserInfoStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(userInfoDic))

    curTs = int(datetime.now().timestamp())
    exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(curTs))

    resData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "userToken": encodedUserInfoStr,
            "timeToken": exToken
        }
    }

    return Response(resData, status.HTTP_200_OK)


@api_view(["POST"])
def testSleep(request):
    postData = request.data

    time.sleep(15)

    resData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "ten": postData.get("fullName"),
            "departmentName": postData.get("phongban"),
            "hello": "goodbye abc"
        }
    }
    return Response(resData, status.HTTP_200_OK)

@api_view(["POST"])
def testNoAuth(request):
    return Response({"authUserSession": global_data.authUserSessionData})

@api_view(["POST"])
def testGetUserSession(request):

    print("ta co Bearer Token : " + request.headers.get("Authorization"))
    userAuthSesData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))

    # test ket noi redis
    # redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
    #                                   , port=project_settings.REDIS_PORT_CENTRALIZED
    #                                   , db=project_settings.REDIS_DATABASE_CENTRALIZED,
    #                                   password=project_settings.REDIS_PASSWORD_CENTRALIZED
    #                                   , decode_responses=True, charset="utf-8")
    #
    # resSetRedisKey = redisInstance.set("myptAuthPhong", "Day la value cua Redis key myptAuthPhong SPIDER MAN", 3600)

    resData = {
        "redisConInfo": {
            "host": project_settings.REDIS_HOST_CENTRALIZED,
            "port": project_settings.REDIS_PORT_CENTRALIZED,
            "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
            "password": project_settings.REDIS_PASSWORD_CENTRALIZED
        },
        "domainName": request.get_host(),
        # "authenRedisValue": redisInstance.get("myptAuthPhong"),
        "authUserSessionData": userAuthSesData,
        # "myptProfileHealthCheckData": healthCheckData
    }

    return Response(resData, status.HTTP_200_OK)



# @api_view(["POST"])
# def importToLSQS(request):
#     # Lay tat ca dong trong bang tro_choi_so_vong_quay_tb
#     sovongquayQs = SoVongQuay.objects.all()
#     sovongquay_ser = SoVongQuaySerializer(sovongquayQs, many=True)
#     sovongquayArr = sovongquay_ser.data
#     for sovongquayRow in sovongquayArr:
#         print(sovongquayRow.get("email") + " ; " + sovongquayRow.get("ho_va_ten") + " ; " + str(sovongquayRow.get("so_vong_quay")))
#         so_vong = sovongquayRow.get("so_vong_quay")
#         if so_vong > 0:
#             count = 1
#             while count <= so_vong:
#                 newLsqs = LichSuQuaySo()
#                 newLsqs.da_trung_giai = "0"
#                 newLsqs.email = sovongquayRow.get("email").lower()
#                 newLsqs.emp_code = sovongquayRow.get("emp_code")
#                 newLsqs.ho_va_ten = sovongquayRow.get("ho_va_ten")
#                 newLsqs.phong_ban = sovongquayRow.get("child_depart")
#                 newLsqs.thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 newLsqs.date = datetime.now().strftime("%Y-%m-%d")
#                 newLsqs.gio = datetime.now().strftime("%H:%M:%S")
#                 newLsqs.uuid = str(uuid.uuid4())
#                 newLsqs.save()
#                 count = count + 1
#
#     return Response({}, status.HTTP_200_OK)