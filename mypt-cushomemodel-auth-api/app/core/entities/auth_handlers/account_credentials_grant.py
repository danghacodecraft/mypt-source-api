from http.entities.sdk_users_handler import SdkUsersHandler
from ..auth_handlers.token_handler import TokenHandler

class AccountCredentialsGrant:
    def genAuthorCode(self, userId, authData, grantId):
        return ""

    def verifyGenToken(self, authData, clientGrant):
        userId = int(authData.get("sdkUserId"))
        print("[AccountCredentialsGrant] lay duoc userId tu post_data (authData) : " + str(userId))
        # get user by userId
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
        #     "isSaveCentralizedStorage": True
        # }
        authData["isSaveCentralizedStorage"] = True
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