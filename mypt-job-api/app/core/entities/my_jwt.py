import jwt
import uuid
from app.configs import app_settings

class MyJwt:
    jwtSecretKey = "UOJNHKzxcxz672bnvghjquvmxjvkjlk"
    jwtAlgorithm = "HS512"

    def __init__(self):
        self.jwtSecretKey = app_settings.JWT_SECRET_KEY

    def createJwtToken(self, payloadData):
        jwtToken = jwt.encode(payloadData, self.jwtSecretKey, algorithm=self.jwtAlgorithm)
        return jwtToken

    def createJtiToken(self, jti, options = {}):
        payloadData = {
            "jti": jti
        }

        if options.get("issuedAt", None) is not None:
            payloadData["iat"] = options.get("issuedAt")

        if options.get("expiration", None) is not None:
            payloadData["exp"] = options.get("expiration")

        jtiToken = jwt.encode(payloadData, self.jwtSecretKey, algorithm=self.jwtAlgorithm)
        return jtiToken

    def decodeJwtToken(self, jwtToken, verifySign = False):
        try:
            # print("da vao day decodeJwtToken day ne nha")
            decodedData = jwt.decode(jwtToken, self.jwtSecretKey, algorithms=self.jwtAlgorithm, options={"verify_signature": verifySign})
            return decodedData
        except Exception as ex:
            pass
        return None
