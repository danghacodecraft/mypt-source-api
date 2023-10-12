import base64
import rsa
import redis
import ast
import json
from rest_framework.viewsets import ViewSet

from app.core.helpers import utils as utHelper
from datetime import datetime
from app.configs import app_settings
from django.conf import settings as project_settings

from ..models.rsa_key import RSAKey
from ..serializers.rsa_key_serializer import RSAKeySerializer
from core.entities.my_rsa_alogrithm import MyRSA
from core.helpers.response import *

from app.core.entities.app_user_token_validator import AppUserTokenValidator
from app.http.entities.sdk_users_handler import SdkUsersHandler
from ..models.oauth_grants import OauthGrants
from ..entities.oauth_client_grants_handler import OauthClientGrantsHandler

from app.core.entities.auth_handlers.account_credentials_grant import AccountCredentialsGrant
from app.core.entities.auth_handlers.refresh_token_grant import RefreshTokenGrant
from app.configs import response_codes

from core.helpers import auth_session_handler as authSessionHandler


class CusHomeModelAuthView(ViewSet):
    def gen_app_key_token(self, request):
        try:
            post_data = request.data
            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                              , port=project_settings.REDIS_PORT_CENTRALIZED
                                              , db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                              password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                              , decode_responses=True, charset='utf-8')
            data_rsa_chm = ast.literal_eval(redisInstance.get('appsRSAKeys'))
            data_rsa_chm = data_rsa_chm[post_data['appId']]
            private_key = rsa.PrivateKey.load_pkcs1(data_rsa_chm['privateKey'])
            public_key = rsa.PublicKey.load_pkcs1(data_rsa_chm['publicKey'])

            # encrypt data with public key
            my_rsa = MyRSA()
            data_encrypt = my_rsa.encrypt(post_data['data'], public_key)
        except Exception as ex:
            return response_data(message=str(ex), status=0)
        return response_data(data_encrypt)


    # API nay phu trach validate App-User-Token, App-Id, Ex-Token trong Header cua Request phai match voi nhau
    # Neu match het, se check user dang nhap vao app có trong bang sdk_users chua
    # Chua co thi se tao 1 user account cho user nay trong bang sdk_users
    # Neu ko match thi cho thoat ra khoi tinh nang mo hinh nha KH luon
    def validate_app_user_token(self, request):
        # lay cac Header : App-User-Token va App-Id
        appUserToken = request.headers.get("App-User-Token")
        encryptedAppId = request.headers.get("App-Id")
        if appUserToken is None or encryptedAppId is None:
            return response_data(None, 3, "Missing data")

        app_user_token_val = AppUserTokenValidator()
        # Goi ham validateAppUserTokenAndAppId() o day de validate App-User-Token va App-Id phai match voi nhau
        resValTokenAndAppId = app_user_token_val.validateAppUserTokenAndAppId(appUserToken, encryptedAppId)
        if resValTokenAndAppId["isValid"] == False:
            return response_data({
                "resValTokenAndAppIdErrorMsg": resValTokenAndAppId["errorMsg"]
            }, 3, "Validate failed")

        # Sau khi validateAppUserTokenAndAppId() passed, validate Ex-Token o day
        exToken = request.headers.get("Ex-Token")
        if exToken is None:
            return response_data(None, 3, "Missing data")

        resValExToken = app_user_token_val.validateExToken(exToken)
        if resValExToken["isValid"] == False:
            return response_data({
                "resValExToken": resValExToken,
                "resValTokenAndAppId": resValTokenAndAppId
            }, 3, "Validate failed")

        # compare appId & accUsername trong resValTokenAndAppId & resValExToken
        if resValTokenAndAppId["appId"] == resValExToken["appId"] and resValTokenAndAppId["accUsername"] == resValExToken["accUsername"]:
            # Check user acc nay (bao gom appId va accUsername) co ton tai chua (bang _sdk_users)
            sdk_users_handler = SdkUsersHandler()
            existedSdkUserAcc = sdk_users_handler.getUserByAccUsername(resValTokenAndAppId["appId"], resValTokenAndAppId["accUsername"])
            # Chuan bi user data Dict de create/update user acc
            userDictForCreateUpdate = {
                "fullName": resValTokenAndAppId["fullName"]
            }

            resCreateSdkUser = None
            if existedSdkUserAcc is not None:
                print("DA TON TAI SDK USER : " + str(existedSdkUserAcc.get("user_id")))
                # print(type(existedSdkUserAcc))
                # print(existedSdkUserAcc)
            else:
                print("DAY LA CASE CREATE SDK USER")
                resCreateSdkUser = sdk_users_handler.createUser(resValTokenAndAppId["appId"], resValTokenAndAppId["accUsername"], userDictForCreateUpdate)

            accUsernameKey = app_user_token_val.getAccountUsernameKeyByAppId(resValTokenAndAppId["appId"])
            sessionTokenData = {
                "startTs": int(datetime.now().timestamp()),
                "appId": resValTokenAndAppId["appId"],
                accUsernameKey: resValTokenAndAppId["accUsername"]
            }
            sessionToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(sessionTokenData))

            return response_data({
                "sessionToken": sessionToken,
                "resValTokenAndAppId": resValTokenAndAppId,
                "resValExToken": resValExToken,
                "existedSdkUserAcc": existedSdkUserAcc,
                "resCreateSdkUser": resCreateSdkUser
            })
        else:
            return response_data({
                "resValTokenAndAppId": resValTokenAndAppId,
                "resValExToken": resValExToken
            }, 3, "Validation is failed because not matched")

    # API nay phu trach tao Access Token & Refresh Token cho SDK user
    def auth_user_token(self, request):
        # return response_data({
        #     "accessToken": "sahgdhjagfhabhfjvghjfgsahjcbashjvsahjfvahsjvfhsajfvbhasjfbvhsajf",
        #     "refreshToken": "qweoqwpeopworpqwoxzcbsfdhsdjfsdbfhebhcbsjabfhefbhsafbhdsfbhdjsfb"
        # })

        post_data = request.data.copy()
        grantType = post_data.get("grantType", None)
        if grantType is None:
            return response_data(None, 3, "Missing data")
        # tim grant id tu param grantType
        oauthGrantModel = OauthGrants()
        grantId = oauthGrantModel.findGrantIdByGrantType(grantType)
        print("lay duoc grant id : " + str(grantId))
        if grantId <= 0:
            return response_data(None, 3, "GrantId is invalid")

        # TODO: tim trong bang chm_auth_oauth_client_grants xem co 1 dong cua clientId va grantId nay hay ko
        ocgHandler = OauthClientGrantsHandler()
        clientGrantInfo = ocgHandler.findByGrantIdAndClientId(grantId, app_settings.OAUTH_CLIENT_ID)
        if clientGrantInfo is None:
            return response_data(None, 3, "ClientId va GrantId not found")

        # return response_data({
        #     "grantId": grantId,
        #     "clientId": app_settings.OAUTH_CLIENT_ID,
        #     "clientGrantInfo": clientGrantInfo
        # })

        # lay cac Header : App-User-Token va App-Id
        appUserToken = request.headers.get("App-User-Token")
        encryptedAppId = request.headers.get("App-Id")
        if appUserToken is None or encryptedAppId is None:
            return response_data(None, 3, "Missing data")

        app_user_token_val = AppUserTokenValidator()
        # Goi ham validateAppUserTokenAndAppId() o day de validate App-User-Token va App-Id phai match voi nhau
        resValTokenAndAppId = app_user_token_val.validateAppUserTokenAndAppId(appUserToken, encryptedAppId)
        if resValTokenAndAppId["isValid"] == False:
            return response_data({
                "resValTokenAndAppIdErrorMsg": resValTokenAndAppId["errorMsg"]
            }, 3, "Validate failed")

        # Check user acc nay (bao gom appId va accUsername) co ton tai chua (bang _sdk_users)
        sdk_users_handler = SdkUsersHandler()
        existedSdkUserAcc = sdk_users_handler.getUserByAccUsername(resValTokenAndAppId["appId"], resValTokenAndAppId["accUsername"])
        if existedSdkUserAcc is None:
            return response_data(None, 3, "User acc not found")

        # chuan bi user info dict de update
        userInfoDictForUpdate = {
            "deviceId": post_data.get("deviceId", None),
            "deviceName": post_data.get("deviceName", None),
            "deviceToken": post_data.get("deviceToken", None),
            "devicePlatform": post_data.get("devicePlatform", None)
        }

        loginToSdk = True
        if grantId == app_settings.ACC_CREDENTIALS_GRANT_ID:
            userInfoDictForUpdate["dateLogin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            loginToSdk = True
        elif grantId == app_settings.REFRESH_TOKEN_GRANT_ID:
            userInfoDictForUpdate["dateLatestRefreshToken"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            loginToSdk = False
        else:
            return response_data(None, 3, "Grant Id is invalid")

        sdkUserId = int(existedSdkUserAcc.get("user_id"))
        resUpdateUser = sdk_users_handler.updateUserInfoByUserId(sdkUserId, userInfoDictForUpdate)

        # check grantId de chon 1 auth handler
        grantChannel = None
        if grantId == app_settings.ACC_CREDENTIALS_GRANT_ID:
            grantChannel = AccountCredentialsGrant()
        elif grantId == app_settings.REFRESH_TOKEN_GRANT_ID:
            grantChannel = RefreshTokenGrant()
        else:
            grantChannel = None

        if grantChannel is None:
            return response_data(None, 3, "No auth channel")

        post_data["sdkUserId"] = sdkUserId
        post_data["loginToSdk"] = loginToSdk
        resVerifyGenToken = grantChannel.verifyGenToken(post_data, clientGrantInfo)
        if resVerifyGenToken.get("resGen") == False:
            # Neu grantType la refresh_token va errorCode la RESPONSE_REFRESH_TOKEN_EXPIRED
            if grantId == app_settings.REFRESH_TOKEN_GRANT_ID and resVerifyGenToken.get("errorCode") == "RESPONSE_REFRESH_TOKEN_EXPIRED":
                print("Refresh token het han! Tao 1 cap Access Token - Refresh Token moi thay vi tra ve statusCode 3!")
                client_grant_info = ocgHandler.findByGrantIdAndClientId(app_settings.ACC_CREDENTIALS_GRANT_ID, app_settings.OAUTH_CLIENT_ID)
                if client_grant_info is None:
                    return response_data(None, 3, "ClientId va GrantId not found")
                accCreGrantChannel = AccountCredentialsGrant()
                res_verify_gen_token = accCreGrantChannel.verifyGenToken(post_data, client_grant_info)
                if res_verify_gen_token.get("resGen") == False:
                    return response_data(None, response_codes.response_codes_data.get(res_verify_gen_token.get("errorCode")).get("code"), "Server busy")
                tokens_data = res_verify_gen_token.get("data")
                return response_data({
                    "accessToken": tokens_data.get("accessToken"),
                    "refreshToken": tokens_data.get("refreshToken"),
                    "accessTokenJti": tokens_data.get("jti")
                })
            else:
                return response_data(None, response_codes.response_codes_data.get(resVerifyGenToken.get("errorCode")).get("code"),"Server busy")

        # return response_data({
        #     "resValTokenAndAppId": resValTokenAndAppId,
        #     "existedSdkUserAcc": existedSdkUserAcc,
        # })

        tokensData = resVerifyGenToken.get("data")
        return response_data({
            "accessToken": tokensData.get("accessToken"),
            "refreshToken": tokensData.get("refreshToken"),
            "accessTokenJti": tokensData.get("jti")
        })

    # API nay de goi private. API nay dung de test generate App-User-Token, App-Id, Ex-Token de dung cho API validate-app-user-token
    # Bo sung generate them SessionToken (khi truyen vao Header la Authorization) de dung cho API auth-user-token
    def gen_app_user_token(self, request):
        post_data = request.data
        appId = post_data.get("appId", None)
        if appId is None:
            return response_data(None, 5, "Missing app ID")

        if appId not in ["mobiqc", "mobinet", "saleclub", "mypt"]:
            return response_data(None, 5, "app ID is invalid")

        accUsername = post_data.get("accUsername", "").strip()
        if accUsername == "":
            return response_data(None, 5, "Missing Account Username")

        if appId == "mobiqc":
            accUsernameKey = "insideAcc"
        elif appId == "mobinet":
            accUsernameKey = "mobinetAcc"
        elif appId == "mypt":
            accUsernameKey = "email"
        else:
            accUsernameKey = "saleclubAcc"

        appUserData = {
            "appId": appId,
            accUsernameKey: accUsername,
            "name": post_data.get("name", "")
        }

        # Lay publicKey tuong ung cua app tu Redis appsRSAKeys
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        appsRsaKeysStr = redisInstance.get("appsRSAKeys")
        if appsRsaKeysStr is None:
            return response_data(None, 6, "No any RSA Keys in cache")

        appsRsaKeys = ast.literal_eval(appsRsaKeysStr)
        if appsRsaKeys is None:
            return response_data(None, 6, "No any valid RSA Keys in cache")

        appRsaKeyData = appsRsaKeys.get(appId, None)
        if appRsaKeyData is None:
            return response_data(None, 6, "No RSA Keys of the app " + appId + " in cache")

        publicKeyStr = appRsaKeyData.get("publicKey", "")
        public_key_obj = rsa.PublicKey.load_pkcs1(publicKeyStr)
        # print(type(public_key))

        print(appUserData)

        # encrypt data with public key
        my_rsa = MyRSA()
        encryptedStr = my_rsa.encrypt(appUserData, public_key_obj)
        # print(encryptedStr)
        appUserToken = encryptedStr

        # generate App-Id (ma hoa appId)
        enc_appId = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, appId)

        # generate Ex-Token
        exTokenData = {
            "curDt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "appId": appId,
            accUsernameKey: accUsername
        }
        exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(exTokenData))

        # generate SessionToken
        sessionTokenData = {
            "startTs": int(datetime.now().timestamp()),
            "appId": appId,
            accUsernameKey: accUsername
        }
        sessionToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(sessionTokenData))

        return response_data({
            "appId": appId,
            "appUserToken": appUserToken,
            "encryptedAppId": enc_appId,
            "exToken": exToken,
            "sessionToken": sessionToken,
            "publicKeyStr": publicKeyStr
        })

    # API nay de goi private
    def decrypt_rsa_token(self, request):
        post_data = request.data
        appId = post_data.get("appId", None)
        rsaToken = post_data.get("rsaToken", None)

        # Lay privateKey tuong ung cua app tu Redis appsRSAKeys
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_CHM_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        appsRsaKeysStr = redisInstance.get("appsRSAKeys")
        if appsRsaKeysStr is None:
            return response_data(None, 6, "No any RSA Keys in cache")

        appsRsaKeys = ast.literal_eval(appsRsaKeysStr)
        if appsRsaKeys is None:
            return response_data(None, 6, "No any valid RSA Keys in cache")

        appRsaKeyData = appsRsaKeys.get(appId, None)
        if appRsaKeyData is None:
            return response_data(None, 6, "No RSA Keys of the app " + appId + " in cache")

        privateKeyStr = appRsaKeyData.get("privateKey", "")
        private_key_obj = rsa.PrivateKey.load_pkcs1(privateKeyStr)

        my_rsa = MyRSA()

        decrypted_str = ""
        try:
            b64_decoded_rsa_token = rsaToken
            decrypted_str = my_rsa.decrypt(b64_decoded_rsa_token, private_key_obj)
        except Exception as ex:
            return response_data(None, 6, "Ko decrypt bang RSA Private Key duoc !")

        try:
            decryptedData = json.loads(decrypted_str)
        except Exception as ex:
            decryptedData = decrypted_str

        print(decryptedData)
        print(type(decryptedData))

        return response_data({
            "decrypted_str": decrypted_str,
            "decryptedData": decryptedData,
            "privateKeyStr": privateKeyStr
        })

    # API nay de goi private
    def decrypt_aes_token(self, request):
        post_data = request.data
        encrypted_str = post_data.get("encrypted_str", None)
        decrypted_str = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, encrypted_str)
        try:
            decryptedData = ast.literal_eval(decrypted_str)
        except Exception as ex:
            decryptedData = decrypted_str

        return response_data({
            "decrypted_str": decrypted_str,
            "decryptedData": decryptedData
        })

    # API nay de goi private
    def test_get_user_session(self, request):
        print("ta co Bearer Token : " + request.headers.get("Authorization"))
        userAuthSesData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        return response_data({
            "userAuthSesData": userAuthSesData
        })