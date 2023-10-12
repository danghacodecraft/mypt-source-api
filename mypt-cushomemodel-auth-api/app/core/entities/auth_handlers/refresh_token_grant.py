from http.entities.sdk_refresh_token_handler import SdkRefreshTokenHandler
from http.entities.sdk_users_handler import SdkUsersHandler
from ..auth_handlers.token_handler import TokenHandler
from app.core.entities.my_jwt import MyJwt
from datetime import datetime
from http.models.sdk_refresh_token import SdkRefreshToken


class RefreshTokenGrant:
    def verifyGenToken(self, authData, clientGrant):
        # check param refreshToken trong POST data (authData)
        if authData.get("refreshToken", None) is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }

        jwtObj = MyJwt()
        # decode refreshToken de lay jti (refresh token id)
        refreshTokenPayloadData = jwtObj.decodeJwtToken(str(authData.get("refreshToken")))
        if refreshTokenPayloadData is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        if refreshTokenPayloadData.get("jti", None) is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        refreshTokenId = refreshTokenPayloadData.get("jti")
        # check refresh token id nay co trong bang oauth_refresh_tokens hay ko
        ortHandler = SdkRefreshTokenHandler()
        refreshTokenInfo = ortHandler.getRefreshTokenById(refreshTokenId)
        if refreshTokenInfo is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        # check sdkUserId
        userId = int(refreshTokenInfo.get("user_id"))
        sdkUserId = int(authData.get("sdkUserId"))
        print("[RefreshTokenGrant] so sanh userId cua refreshTokenInfo va sdkUserId cua authData : " + str(userId) + " ; " + str(sdkUserId))
        if userId != sdkUserId:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }

        if int(refreshTokenInfo.get("revoked")) == 1:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_EXPIRED",
                "data": None
            }
        # check expires_at cua refreshTokenInfo de xem refresh token nay co het han chua
        rtExpireStr = refreshTokenInfo.get("expires_at")
        print(rtExpireStr)
        rtExpireStr = rtExpireStr.replace("T", " ").replace("Z", "")
        print(rtExpireStr)
        rtExpireDt = datetime.strptime(rtExpireStr, "%Y-%m-%d %H:%M:%S")
        rtExpireTs = int(rtExpireDt.timestamp())
        curTs = int(datetime.now().timestamp())
        print("refresh token expire ts : " + str(rtExpireTs) + " ; " + str(curTs))
        if rtExpireTs <= curTs:
            print("Refresh token expired!")
            # update cot revoked cua Refresh Token nay thanh 1
            SdkRefreshToken.objects.filter(id=refreshTokenInfo.get("id")).update(revoked=1,
                                                                                   updated_at=datetime.now().strftime(
                                                                                       "%Y-%m-%d %H:%M:%S"))
            # return
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_EXPIRED",
                "data": None
            }

        # Lay thong tin user tu cot user_id trong bang oauth_refresh_tokens
        sdk_users_handler = SdkUsersHandler()
        userInfo = sdk_users_handler.getUserByUserId(userId)
        if userInfo is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_USER_NOT_FOUND_BY_USER_ID",
                "data": None
            }

        tokenHandlerObj = TokenHandler()
        # chuan bi data de tao token
        # newAuthData = {
        #     "refreshTokenId": refreshTokenInfo.get("id"),
        #     "isSaveCentralizedStorage": True,
        #     "jwtRefreshToken": str(authData.get("refreshToken"))
        # }

        authData["refreshTokenId"] = refreshTokenInfo.get("id")
        authData["isSaveCentralizedStorage"] = True
        authData["jwtRefreshToken"] = str(authData.get("refreshToken"))
        resultGetToken = tokenHandlerObj.genTokenByUser(userInfo, authData, clientGrant)
        print(resultGetToken)

        if resultGetToken is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_GEN_TOKEN_FAILED",
                "data": None
            }

        return {
            "resGen": True,
            "errorCode": None,
            "data": resultGetToken
        }
