import uuid
from app.http.models.sdk_users import SdkUsers
from app.http.serializers.sdk_users_serializer import SdkUsersSerializer
from app.http.models.sdk_access_token import SdkAccessToken
from app.http.models.sdk_refresh_token import SdkRefreshToken
from datetime import datetime
from datetime import timedelta
from app.configs import app_settings
from app.core.entities.my_jwt import MyJwt
import redis
import random
from app.core.entities.centralized_session import CentralizedSession
from app.http.entities.sdk_access_token_handler import SdkAccessTokenHandler
from app.http.entities.sdk_refresh_token_handler import SdkRefreshTokenHandler

from app.http.entities.sdk_permission_handler import *
from django.conf import settings as project_settings


class TokenHandler:
    def genTokenByUser(self, userInfo, authData, clientGrant):
        jwtObj = MyJwt()

        userId = int(userInfo.get("user_id"))
        caseRefreshToken = False
        refreshTokenId = ""
        if authData.get("refreshTokenId", None) is not None:
            caseRefreshToken = True
            refreshTokenId = str(authData.get("refreshTokenId"))
            print("[genTokenByUser] Case refresh token : " + refreshTokenId)

            # CACH 1 : revoke het cac Access Token cua refreshTokenId nay de chuan bi tao Access Token moi tu refreshTokenId nay
            revokeAccessTokensResult = self.revokeAccessTokensByRefreshToken(refreshTokenId)
            if revokeAccessTokensResult["isRevokeAccessTokens"] == False:
                return {
                    "accessToken": jwtObj.createJtiToken(revokeAccessTokensResult["accessTokenId"], {
                        "issuedAt": int(revokeAccessTokensResult["createAt"].timestamp()),
                        "expiration": int(revokeAccessTokensResult["expiresAt"].timestamp())
                    }),
                    "refreshToken": authData["jwtRefreshToken"],
                    "jti": revokeAccessTokensResult["accessTokenId"]
                }

            # CACH 2 : revoke het cac Access Token & Refresh Token hien tai cua userId nay (tru refreshTokenId ra)
            #  neu muon tai 1 thoi diem, 1 email chi login tren 1 device duy nhat
            # revokeTokensResult = self.revokeTokens(userId, True, refreshTokenId)
        else:
            print("[genTokenByUser] Case tao 1 cap Access Token - Refresh Token MOI cho userId nay")
            # revoke het cac Access Token & Refresh Token hien tai cua userId nay neu muon tai 1 thoi diem,
            # 1 email chi login tren 1 device duy nhat
            # revokeTokensResult = self.revokeTokens(userId, False, "")

        # if not revokeTokensResult["isRevokeToken"]:
        #     # curDt = datetime.now()
        #     # accessTokenExpiredDt = curDt + timedelta(minutes=app_settings.EXPIRES_AT_ACCESS_TOKEN)
        #     # accessTokenExpiredDt = curDt + timedelta(minutes=app_settings.EXPIRES_AT_ACCESS_TOKEN)
        #     return {
        #         "accessToken": jwtObj.createJtiToken(revokeAccessTokensResult["accessTokenId"], {
        #             "issuedAt": int(revokeAccessTokensResult["createAt"].timestamp()),
        #             "expiration": int(revokeAccessTokensResult["expiresAt"].timestamp())
        #         }),
        #         "refreshToken": authData["jwtRefreshToken"],
        #         "jti": revokeAccessTokensResult["accessTokenId"]
        #     }

        # TAO access token
        accessTokenModel = SdkAccessToken()
        accessTokenModel.id = self.genUuidForToken("createAccessToken", userId)
        newAccessTokenId = accessTokenModel.id

        accessTokenModel.user_id = userId
        accessTokenModel.app_id = userInfo.get("app_id")
        accessTokenModel.acc_username = userInfo.get("acc_username")
        accessTokenModel.client_id = str(clientGrant.get("client_id"))
        # Neu day la case "Tao lai Access Token tu Refresh Token"
        if caseRefreshToken == True:
            accessTokenModel.refresh_token_id = refreshTokenId
        # set cac field con lai
        accessTokenModel.device_id = userInfo.get("device_id")
        accessTokenModel.device_name = userInfo.get("device_name")
        accessTokenModel.device_token = userInfo.get("device_token")
        accessTokenModel.device_platform = userInfo.get("device_platform")
        accessTokenModel.grant_id = int(clientGrant.get("grant_id"))
        # set login_to_sdk
        if authData["loginToSdk"] == True:
            accessTokenModel.login_to_sdk = 1
        else:
            accessTokenModel.login_to_sdk = 0

        accessTokenModel.revoked = 0

        curDt = datetime.now()
        accessTokenModel.created_at = curDt.strftime("%Y-%m-%d %H:%M:%S")
        accessTokenExpiredDt = curDt + timedelta(minutes=app_settings.EXPIRES_AT_ACCESS_TOKEN)
        # set expires_at
        accessTokenModel.expires_at = accessTokenExpiredDt.strftime("%Y-%m-%d %H:%M:%S")
        # save
        resCreateAccessToken = accessTokenModel.save()

        # TAO refresh token neu day la case "Tao Access Token moi" (khong danh cho case "Tao lai Access Token tu Refresh Token")
        if caseRefreshToken == False:
            refreshTokenModel = SdkRefreshToken()
            refreshTokenModel.id = self.genUuidForToken("getFromRefreshToken", userId)
            refreshTokenId = refreshTokenModel.id
            refreshTokenModel.user_id = userId
            refreshTokenModel.app_id = userInfo.get("app_id")
            refreshTokenModel.acc_username = userInfo.get("acc_username")
            refreshTokenModel.access_token_id = newAccessTokenId
            refreshTokenModel.client_id = str(clientGrant.get("client_id"))
            refreshTokenModel.revoked = 0
            refreshTokenExpiredDt = curDt + timedelta(minutes=app_settings.EXPIRES_AT_REFRESH_TOKEN)
            refreshTokenModel.expires_at = refreshTokenExpiredDt.strftime("%Y-%m-%d %H:%M:%S")
            resCreateRefreshToken = refreshTokenModel.save()
            # lay refresh token moi tao de update vao cot refresh_token_id cua bang oauth_access_tokens
            SdkAccessToken.objects.filter(id=newAccessTokenId).update(refresh_token_id=refreshTokenId,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            # update lai cot access_token_id voi newAccessTokenId cho row oauth_refresh_tokens
            SdkRefreshToken.objects.filter(id=refreshTokenId).update(access_token_id=newAccessTokenId,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # TODO: Luu vao redis, voi key là AccessTokenId
        if authData.get("isSaveCentralizedStorage") == True:
            resSaveCenSession = self.saveCentralizedSession({
                "id": newAccessTokenId,
                "expiresAt": accessTokenExpiredDt
            }, clientGrant, userInfo, authData)
            if resSaveCenSession.get("resSave") == False:
                return None

        # return
        return {
            "accessToken": jwtObj.createJtiToken(newAccessTokenId, {
                "issuedAt": int(curDt.timestamp()),
                "expiration": int(accessTokenExpiredDt.timestamp())
            }),
            "refreshToken": jwtObj.createJtiToken(refreshTokenId),
            "jti": newAccessTokenId
        }

    # revoke het cac Access Token & Refresh Token hien tai cua userId truyen vao
    # Neu day la case "Refresh token" (caseRefreshToken = True) : ko xoa row oauth_refresh_tokens cua refreshTokenId nay
    def revokeTokens(self, userId, caseRefreshToken=False, refreshTokenId=""):
        # Lay ra cac access token (voi revoked = 0) cua userId nay
        oatHandler = SdkAccessTokenHandler()
        accessTokenObjs = oatHandler.getUnRevokedAccessTokensByUser(userId)
        # Neu day la truong hop refresh token, check co access token nao cua refreshTokenId hay ko, neu co thi check
        # tiep access token do con trong Redis hay ko. Neu con thi return lun
        if caseRefreshToken and refreshTokenId:
            print("It is Case refresh token")
            accessTokenObjs = [x for x in accessTokenObjs if x["refresh_token_id"] == refreshTokenId]
            if len(accessTokenObjs) > 0:
                accessTokenObj = accessTokenObjs[0]
                # Kiem tra trong redis co ton tai
                redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                                  port=project_settings.REDIS_PORT_CENTRALIZED,
                                                  db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                                  password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                                  decode_responses=True,
                                                  charset="utf-8")
                user_token_str = redisInstance.get(f'chmsession:{accessTokenObj["id"]}')

                if user_token_str is not None:
                    print(f'>>>>>>>>>>> USER TOKEN: {accessTokenObj["id"]} CON HAN TRONG REDIS VA KHONG TAO MOI')
                    return {
                        "isRevokeToken": False,
                        "accessTokenId": accessTokenObj["id"],
                        "refreshTokenId": accessTokenObj["refresh_token_id"],
                        "createAt":  datetime.strptime(accessTokenObj["created_at"], "%Y-%m-%dT%H:%M:%S"),
                        "expiresAt": datetime.strptime(accessTokenObj["expires_at"], "%Y-%m-%dT%H:%M:%S")
                    }

        # revoke cac access token cua userId nay
        resRevokeAccessTokens = oatHandler.revokeAccessTokensByUser(userId)
        # revoke cac refresh token cua userId nay
        # CHU Y : Neu day la case "Refresh token" (caseRefreshToken = True) : ko xoa row oauth_refresh_tokens cua refreshTokenId nay
        ortHandler = SdkRefreshTokenHandler()
        if caseRefreshToken == True and refreshTokenId != "":
            resRevokeRefreshTokens = ortHandler.revokeRefreshTokensByUser(userId, refreshTokenId)
        else:
            resRevokeRefreshTokens = ortHandler.revokeRefreshTokensByUser(userId)

        # xoa het data cac access token cua userId nay trong Redis
        if accessTokenObjs is not None:
            cenSessionObj = CentralizedSession()
            for accessTokenObj in accessTokenObjs:
                cenSessionObj.removeSession(accessTokenObj.get("id"))

        return {
            "isRevokeToken": True,
            "accessTokenId": "",
            "refreshTokenId": "",
            "createAt": "",
            "expiresAt": ""
        }

    # Ham nay chi dung truong hop refresh token
    # Ham nay xoa het tat ca Access Token cua Refresh Token nay (de chuan bi tao access token moi tu Refresh Token nay)
    def revokeAccessTokensByRefreshToken(self, refreshTokenId):
        # Lay ra cac access token (voi revoked = 0) cua refreshTokenId nay
        oatHandler = SdkAccessTokenHandler()
        accessTokenObjs = oatHandler.getAccessTokensByRefreshTokenId(refreshTokenId)
        if accessTokenObjs is None:
            return {
                "isRevokeAccessTokens": True
            }

        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                          port=project_settings.REDIS_PORT_CENTRALIZED,
                                          db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                          decode_responses=True,
                                          charset="utf-8")
        # check tung Access Token trong accessTokenObjs xem co cai nao con ton tai trong Redis ko
        # Con thi se tiep tuc su dung Access Token nay thay vi tao moi
        for accessTokenObj in accessTokenObjs:
            user_token_str = redisInstance.get("chmsession:" + accessTokenObj.get("id"))
            if user_token_str is not None:
                print("[revokeAccessTokensByRefreshToken] Session data cua JTI : " + accessTokenObj.get("id") + " CON TRONG SESSION REDIS NEN KHONG CAN TAO ACCESS TOKEN MOI")
                return {
                    "isRevokeAccessTokens": False,
                    "accessTokenId": accessTokenObj["id"],
                    "refreshTokenId": accessTokenObj["refresh_token_id"],
                    "createAt": datetime.strptime(accessTokenObj["created_at"], "%Y-%m-%dT%H:%M:%S"),
                    "expiresAt": datetime.strptime(accessTokenObj["expires_at"], "%Y-%m-%dT%H:%M:%S")
                }

        # update revoked thanh 1 trong DB
        print("[revokeAccessTokensByRefreshToken] Update all Access Token cua RefreshTokenId " + refreshTokenId + " : revoked = 1")
        resRevokeAccessTokens = SdkAccessToken.objects.filter(refresh_token_id=refreshTokenId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # xoa het cac key (la cac access token thuoc refreshTokenId) trong Redis
        # cenSessionObj = CentralizedSession()
        # for accessTokenObj in accessTokenObjs:
        #     cenSessionObj.removeSession(accessTokenObj.get("id"))

        return {
            "isRevokeAccessTokens": True
        }

    def saveCentralizedSession(self, accessTokenInfo, clientGrant, userInfo, authData):
        try:
            sessionData = {
                "clientId": str(clientGrant.get("client_id")),
                "grantId": int(clientGrant.get("grant_id")),
                "userId": int(userInfo.get("user_id")),
                "appId": userInfo.get("app_id"),
                "accUsername": userInfo.get("acc_username"),
                "email": userInfo.get("email", ""),
                "fullName": userInfo.get("full_name", ""),
                "deviceId": userInfo.get("device_id", ""),
                "deviceName": userInfo.get("device_name", ""),
                "deviceToken": userInfo.get("device_token", ""),
                "devicePlatform": userInfo.get("device_platform", ""),
                "empCode": "",
                # "birthday": "",
                # "sex": "",
                "permissions": {},
                # "featuresRoles": {}
            }

            # Tap hop cac phong ban (child_depart) ma user nay co quyen tuong tac de gui qua mypt-ho-profile-api de lay parent_depart, branch cua tung child_depart
            perHandler = SdkPermissionHandler()
            persData = perHandler.getAllPermissionsByUser(int(userInfo.get("user_id")))
            permissionsData = persData.get("persData")
            sessionData["permissions"] = permissionsData

            expiresAtTs = int(accessTokenInfo.get("expiresAt").timestamp())
            seconds = expiresAtTs - int(datetime.now().timestamp())

            cenSessionObj = CentralizedSession()
            resSaveSession = cenSessionObj.saveSession(accessTokenInfo.get("id"), sessionData, seconds)
            return resSaveSession
        except Exception as e:
            print(e)

    def genUuidForToken(self, tokenType, userId):
        uuidStr = uuid.uuid4()
        return str(uuidStr)
