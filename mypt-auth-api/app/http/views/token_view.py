import threading
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ...myCore.helpers.response import *
import jwt
from app.myHttp.models.user_infos import UserInfos
from app.myHttp.serializers.user_infos_serializer import UserInfosSerializer
from app.myHttp.models.oauth_grants import OauthGrants
from app.myHttp.serializers.oauth_grants_serializer import OauthGrantsSerializer
import uuid
import ast
import json
from app.configs import app_settings
from app.myCore.helpers import utils as utHelper
from app.myHttp.Entities.user_infos_handler import UserInfosHandler
from app.myHttp.Entities.oauth_client_grants_handler import OauthClientGrantsHandler
from app.myCore.Entities.authHandlers.fpt_adfs import FptAdfs
from app.myCore.Entities.authHandlers.account_credentials_grant import AccountCredentialsGrant
from app.myCore.Entities.OAuth.refresh_token import RefreshToken
from datetime import datetime
from datetime import timedelta
from app.myCore.Entities.my_jwt import MyJwt
import redis
import random
from app.configs import response_codes
import requests
from django.conf import settings


# Create your views here.
@api_view(["POST"])
def genUserToken(request):

    # print("vao API user token day")

    # curTsStr = str(datetime.now().timestamp())
    # rd1 = random.randint(1, 9999999)
    # rd2 = random.randint(1, 9999999)
    # str1 = "abc123456789123" + curTsStr + "-" + str(rd1)
    # str2 = "abc123456789123" + curTsStr + "-" + str(rd2)
    # uuid5Str1 = uuid.uuid5(uuid.NAMESPACE_DNS, str1)
    # uuid5Str2 = uuid.uuid5(uuid.NAMESPACE_DNS, str2)
    #
    # respondedData = {
    #     "statusCode": 0,
    #     "message": "OK",
    #     "data": {
    #         "curTsStr": curTsStr,
    #         "str1": str1,
    #         "str2": str2,
    #         "uuid5Str1": uuid5Str1,
    #         "uuid5Str2": uuid5Str2
    #     }
    # }
    # return Response(respondedData, status.HTTP_200_OK)

    postData = request.data
    device_data = request.data.copy()
    encodedUserTokenStr = postData.get("userToken")

    # decode param userToken de lay ra email & name de luu vao bang user_infos
    userTokenDataStr = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, encodedUserTokenStr)
    print("user token data str sau khi decrypt : " + userTokenDataStr)
    userTokenData = ast.literal_eval(userTokenDataStr)
    userEmail = userTokenData.get("email").lower()
    userFullName = userTokenData.get("name")

    # tim grant id tu param grantType
    oauthGrantModel = OauthGrants()
    grantType = postData.get("grantType")
    grantId = oauthGrantModel.findGrantIdByGrantType(grantType)
    print("lay duoc grant id : " + str(grantId))

    # TODO: tim trong bang oauth_client_grants xem co 1 dong cua clientId va grantId nay hay ko
    ocgHandler = OauthClientGrantsHandler()
    clientGrantInfo = ocgHandler.findByGrantIdAndClientId(grantId, app_settings.OAUTH_CLIENT_ID)
    if clientGrantInfo is None:
        return response_data(None, 6, "ClientId va GrantId not found")

    # return response_data({"grantId": grantId, "clientGrantInfo": clientGrantInfo, "email": userEmail, "name": userFullName})

    # check user
    userInfosHandlerObj = UserInfosHandler()
    # tim xem email nay da co trong bang user_infos hay chua
    userId = 0
    userInfo = userInfosHandlerObj.getUserByEmail(userEmail)
    # chuan bi user info dict de create/update
    userInfoDictForCreateUpdate = {
        "fullName": userFullName,
        "deviceId": postData.get("deviceId", None),
        "deviceName": postData.get("deviceName", None),
        "deviceToken": postData.get("deviceToken", None),
        "devicePlatform": postData.get("devicePlatform", None),
        "lang": postData.get("lang", "vi"),
        "appVersion": postData.get("appVersion", "")
    }
    if grantId == 9 or grantId == 10:
        userInfoDictForCreateUpdate["dateLogin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif grantId == 5:
        userInfoDictForCreateUpdate["dateLatestRefreshToken"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print(userInfoDictForCreateUpdate)

    if userInfo is not None:
        userId = int(userInfo.get("user_id"))
        # print("DAY LA CASE UPDATE USER " + str(userId))
        resUpdateUser = userInfosHandlerObj.updateUserInfoByUserId(userId, userInfoDictForCreateUpdate)
    else:
        # print("DAY LA CASE TAO USER MOI")
        resCreateUser = userInfosHandlerObj.createUser(userEmail, userInfoDictForCreateUpdate)
        if resCreateUser.get("resCreate") == "SUCCESS":
            userId = resCreateUser.get("userId")
        else:
            return response_data(None, 6, "Create user failed")

    # check user id
    # print("ta co user id : " + str(userId))
    if userId <= 0:
        return response_data(None, 6, "User not created")

    # check grantId
    channel = None
    if grantId == 9:
        channel = FptAdfs()
    elif grantId == 10:
        channel = AccountCredentialsGrant()
    elif grantId == 5:
        channel = RefreshToken()
    else:
        channel = None

    if channel is None:
        return response_data(None, 6, "No auth channel")

    # Tao author code truoc (bang oauth_auth_codes)

    # add them userId vao postData truoc khi gen token
    postData["userId"] = userId
    resVerifyGenToken = channel.verifyGenToken(postData, clientGrantInfo)
    if resVerifyGenToken.get("resGen") == False:
        return response_data(None, response_codes.response_codes_data.get(resVerifyGenToken.get("errorCode")).get("code"), "Server busy")
    device_data = {
        "email": userEmail,
        "device_id": device_data.get("deviceId", None),
        "device_name": device_data.get("deviceName", None),
        "device_token": device_data.get("deviceToken", None),
        "device_platform": device_data.get("devicePlatform", None)
    }
    tokenData = resVerifyGenToken.get("data")

    return response_data({
        "accessToken": tokenData.get("accessToken"),
        "refreshToken": tokenData.get("refreshToken")
    })