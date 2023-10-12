from app.configs import app_settings


class SalaryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        print("[middleware " + className + "] goi truoc khi response : " + curUrl)
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        for routeUrl in routesMiddlewareData:
            if curUrl == routeUrl:
                middlewareApplied = True

        if middlewareApplied == False:
            print("route " + curUrl + " ko duoc apply middleware " + className)
            response = self.get_response(request)
            return response

        excepRespondedData = {
            "statusCode": 5,
            "message": "Input Invalid",
            "data": None
        }
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
