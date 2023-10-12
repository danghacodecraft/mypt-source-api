from app.http.models.oauth_access_token import OauthAccessToken
from app.http.serializers.oauth_access_token_serializer import OauthAccessTokenSerializer
from datetime import datetime

class OauthAccessTokenHandler:
    def getAccessTokensByRefreshTokenId(self, userId, refreshTokenId):
        print("chuan bi tim cac AccessToken theo RefreshTokenId : " + str(userId) + " ; " + refreshTokenId)
        oatQs = OauthAccessToken.objects.filter(user_id=userId, refresh_token_id=refreshTokenId, revoked=0)
        oat_ser = OauthAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr
        else:
            return None

    def getUnRevokedAccessTokensByUser(self, userId):
        print("chuan bi tim cac AccessToken theo UserId : " + str(userId))
        oatQs = OauthAccessToken.objects.filter(user_id=userId, revoked=0).order_by("-created_at")
        oat_ser = OauthAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr
        else:
            return None

    def revokeAccessTokensByUser(self, userId):
        rowsUpdated = OauthAccessToken.objects.filter(user_id=userId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated

    def getAccessTokenById(self, accessTokenId):
        print("chuan bi tim row AccessToken theo ID : " + accessTokenId)
        oatQs = OauthAccessToken.objects.filter(id=accessTokenId)[0:1]
        oat_ser = OauthAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr[0]
        else:
            return None

    def revokeAccessTokenById(self, accessTokenId):
        rowsUpdated = OauthAccessToken.objects.filter(id=accessTokenId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated