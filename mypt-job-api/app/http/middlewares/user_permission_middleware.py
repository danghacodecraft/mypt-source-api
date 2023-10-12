from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from datetime import datetime
from django.conf import settings as project_settings
from app.configs import app_settings
from app.core.helpers import utils as utHelper
from core.helpers import auth_session_handler as authSessionHandler
import redis
import ast
import json


class UserPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        if curUrl in routesMiddlewareData:
            middlewareApplied = True

        if middlewareApplied == False:
            response = self.get_response(request)
            return response

        excepRespondedData = {
            "statusCode": 6,
            "message": "No permission for this API",
            "data": None
        }

        # Check URL hien tai dang duoc map voi permission nao (check trong Redis centralized)
        apiRoute = curUrl.replace("/" + app_settings.SERVICE_NAME + "/", "")

        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        permissionsWithRoutesStr = redisInstance.get("permissionsWithRoutes")
        if permissionsWithRoutesStr is None:
            excepRespondedData["message"] = "No permission with route data"
            return JsonResponse(excepRespondedData)

        permissionsWithRoutesData = ast.literal_eval(permissionsWithRoutesStr)

        if permissionsWithRoutesData.get(app_settings.SERVICE_NAME, None) is None:
            excepRespondedData["message"] = "No service in permission with route data"
            return JsonResponse(excepRespondedData)

        servicePersRoutes = permissionsWithRoutesData[app_settings.SERVICE_NAME]
        if servicePersRoutes.get(apiRoute, None) is None:
            excepRespondedData["message"] = "No API route in service in permission with route data"
            return JsonResponse(excepRespondedData)

        perCodesByApiRoute = servicePersRoutes[apiRoute]

        # check permisssions trong User session xem co quyen tinh nang nay ko
        userPerCode = ""
        userPerData = {}
        authSessionData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        userPersData = authSessionData["permissions"]
        # Neu trong permissions co quyen ALL
        userHasRight = False
        if userPersData.get("ALL", None) is not None:
            userHasRight = True
            userPerCode = "ALL"
            userPerData = userPersData.get("ALL")
        else:
            # di qua tung permission trong perCodesByApiRoute
            for perCodeByApiRoute in perCodesByApiRoute:
                if userPersData.get(perCodeByApiRoute, None) is not None:
                    userHasRight = True
                    userPerCode = perCodeByApiRoute
                    userPerData = userPersData.get(perCodeByApiRoute)
                    break

        if not userHasRight:
            excepRespondedData["message"] = "Bạn không có quyền thực hiện tính năng này!"
            return JsonResponse(excepRespondedData)

        # tiep theo la check quyen phong ban (neu has_depart_right = 1)
        if userPerData["has_depart_right"] == 1:
            # check trong input cua API co param childDepart (danh sach bo phan) hay ko
            decodedBodyDataStr = ""
            bodyDataStr = request.body
            try:
                decodedBodyDataStr = bodyDataStr.decode("utf-8")
            except Exception as ex:
                decodedBodyDataStr = ""

            if decodedBodyDataStr == "":
                response = self.get_response(request)
                return response

            bodyParams = None
            try:
                bodyParams = json.loads(decodedBodyDataStr)
            except Exception as ex:
                bodyParams = None


            if bodyParams is None:
                response = self.get_response(request)
                return response

            childDepartsParamArr = bodyParams.get("childDepart", None)
            if childDepartsParamArr is None:
                response = self.get_response(request)
                return response
                # excepRespondedData["message"] = "Missing child departs"
                # return JsonResponse(excepRespondedData)

           
            if len(childDepartsParamArr) <= 0:
               
                response = self.get_response(request)
                return response
                # excepRespondedData["message"] = "Empty child departs"
                # return JsonResponse(excepRespondedData)

            hoRedisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                                , port=project_settings.REDIS_PORT_CENTRALIZED
                                                , db=project_settings.REDIS_HO_DATABASE_CENTRALIZED,
                                                password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                                , decode_responses=True, charset="utf-8")
            allDepartsWithLevels = None
            allDepartsWithLevelsStr = hoRedisInstance.get("allDepartsWithLevels")
            if allDepartsWithLevelsStr is None:
                allDepartsWithLevels = None
            else:
                allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)

            if allDepartsWithLevels is None:
                excepRespondedData["message"] = "Missing data"
                return JsonResponse(excepRespondedData)

            # check tung child depart trong childDepartsParamArr : xem permission nay co apply cho cac child depart nay ko
            hasRightOnChildDeparts = True
            for childDepartParam in childDepartsParamArr:
                childDepartParam = str(childDepartParam)
                hasRightOnChildDepart = False
                # check child_depart_rights truoc
                for parentDepart, childDepartsByParent in userPerData["child_depart_rights"].items():
                    if childDepartParam in childDepartsByParent:
                        hasRightOnChildDepart = True
                        break

                # Neu check xong trong child_depart_rights ma hasRightOnChildDepart van bang False thi check tiep trong branch_rights
                if hasRightOnChildDepart == False:
                    # check tren TIN
                    if "ALL" in userPerData["branch_rights"]["TIN"]:
                        for parent_depart, child_departs_by_parent in allDepartsWithLevels["allDeparts"]["ALLTIN"].items():
                            if childDepartParam in child_departs_by_parent:
                                hasRightOnChildDepart = True
                                break
                    

                    # Neu hasRightOnChildDepart van bang False thi check tren PNC
                    if hasRightOnChildDepart == False and "ALL" in userPerData["branch_rights"]["PNC"]:
                        for parent_depart, child_departs_by_parent in allDepartsWithLevels["allDeparts"]["ALLPNC"].items():
                            if childDepartParam in child_departs_by_parent:
                                hasRightOnChildDepart = True
                                break
                   

                if hasRightOnChildDepart == False:
                    hasRightOnChildDeparts = False
                    break
               

            if hasRightOnChildDeparts == False:
                excepRespondedData["message"] = "No right on child depart(s)"
                return JsonResponse(excepRespondedData)
            
       

        response = self.get_response(request)
        return response

    def checkChildDepartExistInParent(self, childDepart):
        pass

    def process_request(self, request):
        print("vao process request")

        return None

    def process_response(self, request, response):
        print('vao process response')

        return None
