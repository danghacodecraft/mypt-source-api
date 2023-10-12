import redis
from django.conf import settings as project_settings
from django.http import JsonResponse

from app.configs import app_settings
from app.core.entities.app_user_token_validator import AppUserTokenValidator

# Middleware nay se check App-User-Token, App-Id, Authorization (value la sessionToken) trong Header cua Request phai match voi nhau
# Neu ko match thi cho thoat ra khoi tinh nang mo hinh nha KH luon
class AppUserAndSessionTokenMiddleware:
    app_key = app_settings.APP_KEY_MIDDLEWARE
    redis_instance = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        print("[" + className + "] URL API hien tai : " + curUrl + " ; middleware class name : " + className)
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        print(routesMiddlewareData)

        if curUrl in routesMiddlewareData:
            print("[" + className + "] Route " + curUrl + " duoc apply middleware nay !")
            middlewareApplied = True

        if middlewareApplied == False:
            print("[" + className + "] Route " + curUrl + " KHONG duoc apply middleware nay!")
            response = self.get_response(request)
            return response

        # print("[" + className + "] Route " + curUrl + " duoc di tiep middleware nay !")
        # response = self.get_response(request)
        # return response

        # lay cac Header : App-User-Token va App-Id
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
        if resValTokenAndAppId["isValid"] == False:
            return JsonResponse({
                'statusCode': 3,
                'message': 'Validate tokens failed',
                'data': {
                    "resValTokenAndAppIdErrorMsg": resValTokenAndAppId["errorMsg"]
                }
            })
        # print(resValTokenAndAppId)
        # neu App-User-Token va App-Id match voi nhau, tiep theo la validate Authorization (value la sessionToken)
        session_token = request.headers.get("Authorization")
        if session_token is None:
            return JsonResponse({
                'statusCode': 3,
                'message': 'Missing session token',
                'data': None
            })
        resValSessionToken = app_user_token_val.validateSessionToken(session_token)
        if resValSessionToken["isValid"] == False:
            return JsonResponse({
                'statusCode': 3,
                'message': 'Validate session token failed',
                'data': {
                    "resValSessionToken": resValSessionToken,
                    "resValTokenAndAppId": resValTokenAndAppId
                }
            })

        # compare appId & accUsername trong resValTokenAndAppId & resValSessionToken
        if resValTokenAndAppId["appId"] == resValSessionToken["appId"] and resValTokenAndAppId["accUsername"] == resValSessionToken["accUsername"]:
            print("validate AppUserToken - AppId and SessionToken OK !")
            print(resValTokenAndAppId)
            print(resValSessionToken)
            response = self.get_response(request)
            return response
        else:
            return JsonResponse({
                'statusCode': 3,
                'message': 'Validate AppUserToken - AppId and SessionToken failed because not matched',
                'data': {
                    "resValTokenAndAppId": resValTokenAndAppId,
                    "resValSessionToken": resValSessionToken
                }
            })

        # response = self.get_response(request)
        # return response

    def process_request(self, request):
        print('vao process request')

        return None

    def process_response(self, request, response):
        print('vao process response')

        return None
