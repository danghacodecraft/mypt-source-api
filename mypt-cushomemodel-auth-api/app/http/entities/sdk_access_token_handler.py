from app.http.models.sdk_access_token import SdkAccessToken
from app.http.serializers.sdk_access_token_serializer import SdkAccessTokenSerializer
from datetime import datetime

class SdkAccessTokenHandler:
    def getAccessTokensByRefreshTokenId(self, refreshTokenId):
        print("chuan bi tim cac AccessToken theo RefreshTokenId : " + refreshTokenId)
        oatQs = SdkAccessToken.objects.filter(refresh_token_id=refreshTokenId, revoked=0).order_by("-created_at")
        oat_ser = SdkAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr
        else:
            return None

    def getUnRevokedAccessTokensByUser(self, userId):
        print("chuan bi tim cac AccessToken theo UserId : " + str(userId))
        oatQs = SdkAccessToken.objects.filter(user_id=userId, revoked=0).order_by("-created_at")
        oat_ser = SdkAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr
        else:
            return None

    def revokeAccessTokensByUser(self, userId):
        rowsUpdated = SdkAccessToken.objects.filter(user_id=userId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated

    def getAccessTokenById(self, accessTokenId):
        print("chuan bi tim row AccessToken theo ID : " + accessTokenId)
        oatQs = SdkAccessToken.objects.filter(id=accessTokenId)[0:1]
        oat_ser = SdkAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr[0]
        else:
            return None

    def revokeAccessTokenById(self, accessTokenId):
        rowsUpdated = SdkAccessToken.objects.filter(id=accessTokenId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated