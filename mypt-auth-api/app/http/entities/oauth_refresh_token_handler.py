from app.http.models.oauth_refresh_token import OauthRefreshToken
from app.http.serializers.oauth_refresh_token_serializer import OauthRefreshTokenSerializer
from datetime import datetime

class OauthRefreshTokenHandler:
    def getRefreshTokenById(self, refreshTokenId):
        print("chuan bi tim Refresh Token theo id : " + refreshTokenId)
        ortQs = OauthRefreshToken.objects.filter(id=refreshTokenId)[0:1]
        ort_ser = OauthRefreshTokenSerializer(ortQs, many=True)
        ortArr = ort_ser.data
        if len(ortArr) > 0:
            ortItem = ortArr[0]
            print(ortItem)
            return ortItem
        else:
            return None

    def revokeRefreshTokensByUser(self, userId, exceptRefreshTokenId = ""):
        if exceptRefreshTokenId != "":
            print("revoke refresh token cua user " + str(userId) + " nhung loai tru RF Token id " + str(exceptRefreshTokenId))
            rowsUpdated = OauthRefreshToken.objects.filter(user_id=userId, revoked=0).exclude(id=exceptRefreshTokenId).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            print("revoke tat ca refresh token cua user " + str(userId))
            rowsUpdated = OauthRefreshToken.objects.filter(user_id=userId, revoked=0).update(revoked=1, updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated


    def revokeRefreshTokenById(self, refreshTokenId):
        rowsUpdated = OauthRefreshToken.objects.filter(id=refreshTokenId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated