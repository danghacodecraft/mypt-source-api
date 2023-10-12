import threading
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from http.helpers.response import *
import jwt
from app.http.models.user_infos import UserInfos
from app.http.serializers.user_infos_serializer import UserInfosSerializer
from app.http.models.oauth_grants import OauthGrants
from app.http.serializers.oauth_grants_serializer import OauthGrantsSerializer
import uuid
import ast
import json
from app.configs import app_settings
from app.core.helpers import utils as utHelper
from app.http.Entities.user_infos_handler import UserInfosHandler
from app.http.Entities.oauth_client_grants_handler import OauthClientGrantsHandler
from app.core.Entities.authHandlers.fpt_adfs import FptAdfs
from app.core.Entities.authHandlers.account_credentials_grant import AccountCredentialsGrant
from app.core.Entities.OAuth.refresh_token import RefreshToken
from datetime import datetime
from app.configs import response_codes


# Create your views here.
@api_view(["POST"])
def genUserToken(request):

    postData = request.data
    device_data = request.data.copy()
    encodedUserTokenStr = postData.get("userToken")

    # decode param userToken de lay ra email & name de luu vao bang user_infos
    userTokenDataStr = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, encodedUserTokenStr)
    userTokenData = ast.literal_eval(userTokenDataStr)
    userEmail = userTokenData.get("email").lower()
    userFullName = userTokenData.get("name")

    # tim grant id tu param grantType
    oauthGrantModel = OauthGrants()
    grantType = postData.get("grantType")
    grantId = oauthGrantModel.findGrantIdByGrantType(grantType)

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