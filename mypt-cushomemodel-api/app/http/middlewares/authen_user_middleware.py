from datetime import datetime
from django.http import JsonResponse
from app.configs import app_settings
from app.core.entities.app_user_token_validator import AppUserTokenValidator
from app.core.entities.centralized_session import CentralizedSession
from app.core.helpers import utils as utHelper


class AuthenUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        print("[" + className + "] URL API hien tai : " + curUrl + "middleware class name : " + className)
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        if curUrl in routesMiddlewareData:
            print("[" + className + "] Route " + curUrl + " duoc apply middleware nay !")
            middlewareApplied = True

        if not middlewareApplied:
            print("[" + className + "] route " + curUrl + " KHONG duoc apply middleware nay!")
            response = self.get_response(request)
            return response

        # redis_session_expired (code = 7) : SDK goi API auth-user-token (voi grantType=refresh_token) de tao lai Access Token moi tu Refresh Token hien tai
        # access_token_failed (code = 3) : thoat ra khoi SDK
        errorCodes = {
            "access_token_failed": 3,
            "redis_session_expired": 7,
        }

        # lay cac Header : App-User-Token va App-Id de chuan bi validate App-User-Token va App-Id
        appUserToken = request.headers.get("App-User-Token")
        encryptedAppId = request.headers.get("App-Id")
        if appUserToken is None or encryptedAppId is None:
            return JsonResponse({
                'statusCode': 3,
                'message': 'Missing tokens',
                'data': None
            })
        app_user_token_val = AppUserTokenValidator()
        # validate App-User-Token va App-Id phai match voi nhau
        resValTokenAndAppId = app_user_token_val.validateAppUserTokenAndAppId(appUserToken, encryptedAppId)
        if not resValTokenAndAppId["isValid"]:
            return JsonResponse({
                'statusCode': 3,
                'message': 'Validate tokens failed',
                'data': {
                    "resValTokenAndAppIdErrorMsg": resValTokenAndAppId["errorMsg"]
                }
            })

        # return JsonResponse({
        #         'statusCode': 1,
        #         'message': 'Success',
        #         'data': {
        #             "resValTokenAndAppId": resValTokenAndAppId
        #         }
        #     })

        # Lay header : Authorization
        headerAuthToken = request.headers.get("Authorization")
        if headerAuthToken is None:
            return JsonResponse({
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is none",
                "data": None
            })
        headerAuthToken = str(headerAuthToken)
        print("[" + className + "] Bearer header auth token : " + headerAuthToken)
        if headerAuthToken == "":
            return JsonResponse({
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Bearer Token is empty",
                "data": None
            })

        # remove Bearer
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        if newHeaderAuthToken == "":
            return JsonResponse({
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is empty",
                "data": None
            })

        print("[" + className + "] New header auth token : " + newHeaderAuthToken)

        # validate session
        cenSessionObj = CentralizedSession()
        resValidateSession = cenSessionObj.validateSession(newHeaderAuthToken)
        if resValidateSession.get("errorCode") != "no_error":
            errorCode = resValidateSession.get("errorCode")
            errorResData = None
            if errorCode == "redis_session_expired":
                print("day la case Redis Session Expired : can tra them sessionToken")

                accUsernameKey = app_user_token_val.getAccountUsernameKeyByAppId(resValTokenAndAppId["appId"])
                sessionTokenData = {
                    "startTs": int(datetime.now().timestamp()),
                    "appId": resValTokenAndAppId["appId"],
                    accUsernameKey: resValTokenAndAppId["accUsername"]
                }
                sessionToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(sessionTokenData))
                errorResData = {
                    "sessionToken": sessionToken
                }

            excepRespondedData = {
                "statusCode": errorCodes.get(errorCode),
                "message": resValidateSession.get("errorMsg"),
                "data": errorResData
            }
            return JsonResponse(excepRespondedData)
        else:
            # Check appId va accUsername trong Redis session co match voi data trong resValTokenAndAppId ko
            sessionData = resValidateSession.get("sessionData")
            request.user_auth_session_data = sessionData
            print("[" + className + "] Da lay duoc Session data trong Redis :")
            print("[" + className + "] Chuan bi so sanh sessionData va resValTokenAndAppId : " + sessionData["appId"] + " ; " + resValTokenAndAppId["appId"] + " --- " + sessionData["accUsername"] + " ; " + resValTokenAndAppId["accUsername"])
            if sessionData["appId"] == resValTokenAndAppId["appId"] and sessionData["accUsername"] == resValTokenAndAppId["accUsername"]:
                print("[" + className + "] appId va accUsername trong sessionData va resValTokenAndAppId da MATCH voi nhau ! Cho phép di tiep API chinh !")
                response = self.get_response(request)
                return response
            else:
                return JsonResponse({
                    "statusCode": errorCodes.get("access_token_failed"),
                    "message": "Data not matched",
                    "data": None
                })

    def process_request(self, request):
        print("vao process request")
        return None

    def process_response(self, request, response):
        print('vao process response')
        return None
