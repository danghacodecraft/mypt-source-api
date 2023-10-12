from datetime import datetime

from django.http import JsonResponse

from app.configs import app_settings
from app.core.entities.centralized_session import CentralizedSession
from app.core.helpers import utils as utHelper
from app.http.entities import global_data


class AuthenUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        # print("[" + className + "] URL API hien tai : " + curUrl)
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        if curUrl in routesMiddlewareData:
            # print("[" + className + "] Da tim thay route : " + curUrl + " trong MIDDLEWARE_APPLIED_FOR_ROUTES. Duoc apply middleware nay !")
            middlewareApplied = True

        if middlewareApplied == False:
            # print("route " + curUrl + " KHONG duoc apply middleware " + className)
            response = self.get_response(request)
            return response

        # redis_session_expired (code = 7) : app goi API user-token (voi grantType=refresh_token) de tao lai Access Token tu Refresh Token
        # access_token_failed (code = 3) : quay ve man hinh Login
        # connect_redis_failed (code = 8) : hien popup thong bao loi
        errorCodes = {
            "access_token_failed": 3,
            "redis_session_expired": 7,
            "connect_redis_failed": 8
        }

        headerAuthToken = request.headers.get("Authorization")
        # print("[middleware " + className + "] ta co Bearer header auth token : " + str(headerAuthToken))

        if headerAuthToken is None:
            excepRespondedData = {
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is none",
                "data": None
            }
            return JsonResponse(excepRespondedData)

        headerAuthToken = str(headerAuthToken)
        if headerAuthToken == "":
            excepRespondedData = {
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is empty",
                "data": None
            }
            return JsonResponse(excepRespondedData)

        # remove Bearer
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        # print("[middleware " + className + "] new header auth token : " + newHeaderAuthToken)
        if newHeaderAuthToken == "":
            excepRespondedData = {
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is empty",
                "data": None
            }
            return JsonResponse(excepRespondedData)

        # validate session
        cenSessionObj = CentralizedSession()
        resValidateSession = cenSessionObj.validateSession(newHeaderAuthToken)
        if resValidateSession.get("errorCode") != "no_error":
            errorCode = resValidateSession.get("errorCode")
            errorResData = None
            if errorCode == "redis_session_expired":
                # print("day la case Redis Session Expired : can tra them extoken")
                exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(int(datetime.now().timestamp())))
                errorResData = {
                    "extoken": exToken
                }

            excepRespondedData = {
                "statusCode": errorCodes.get(errorCode),
                "message": resValidateSession.get("errorMsg"),
                "data": errorResData
            }
            return JsonResponse(excepRespondedData)

        response = self.get_response(request)
        return response

    def process_request(self, request):
        print("vao process request")
        return None

    def process_response(self, request, response):
        print('vao process response')
        return None
