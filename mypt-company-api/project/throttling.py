from abc import ABC

from rest_framework import throttling
from app.configs import variable
from app.core.helpers.response import *
from rest_framework.views import exception_handler


class CustomThrottle(throttling.SimpleRateThrottle, ABC):
    def parse_rate(self, rate):
        if rate is None:
            return None, None
        num, period = rate.split(variable.THROTTLING['split'])
        num_requests = int(num)
        duration = {variable.THROTTLING['per_time'][-1]: int(variable.THROTTLING['per_time'][:-1])}[period[0]]
        return num_requests, duration

    def allow_request(self, request, view):
        if request.method in variable.THROTTLING['method']:
            return True
        return super().allow_request(request, view)


class UserThrottle(CustomThrottle, throttling.UserRateThrottle):
    rate = variable.THROTTLING['rate'] + variable.THROTTLING['split'] + variable.THROTTLING['per_time'][-1]


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    else:
        response = exc.detail
    return response_data(message=response, status=0, data=None)
