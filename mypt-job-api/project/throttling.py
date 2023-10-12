import json
from rest_framework.throttling import UserRateThrottle

from pytimeparse.timeparse import timeparse
from rest_framework import throttling
from app.core.helpers.auth_session_handler import getUserAuthSessionData



def debounce_name(request):
    str_name = request.get_full_path()
    str_name = str_name.split("/")[-1]
    str_result = str_name + json.dumps(request.data).replace(" ", "")
    return str_result


class SalaryUserRateThrottle(UserRateThrottle):
    scope = 'salary'
    rate = '1/second'

    def get_cache_key(self, request, view):
        super().get_cache_key(request, view)
        if request.user and request.user.is_authenticated:
            ident = request.user.pk + debounce_name(request)
        else:
            ident = self.get_ident(request) + debounce_name(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class SalaryCronCallUserRateThrottle(SalaryUserRateThrottle):
    scope = 'salary'
    rate = '1/minute'

    def get_cache_key(self, request, view):
        super().get_cache_key(request, view)
        if request.user and request.user.is_authenticated:
            ident = request.user.pk + debounce_name(request)
        else:
            ident = self.get_ident(request) + debounce_name(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
        
class MyPTUserThrottle(throttling.UserRateThrottle):
    scope = 'mypt_user'
    cache_format = 'throttle:%(scope)s:%(ident)s'
    
    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = timeparse(period) 
        return (num_requests, duration)

    def debounce_name(self, request):
        str_name = request.get_full_path()
        return str_name
    
    def allow_request(self, request, view):
        if request.method == 'GET':
            return True
        
        authorization = request.headers.get("Authorization", None)
        
        if not authorization:
            return self.throttle_failure()
        
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        super().get_cache_key(request, view)
        if request.user and request.user.is_authenticated:
            ident = request.user.pk + self.debounce_name(request)
        else:
            ident = f"{self.get_ident(request)}_{self.debounce_name(request)}"

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
        
    def get_ident(self, request):
        authorization = request.headers.get("Authorization", None)
        session = getUserAuthSessionData(authorization)
        return session["userId"]
    
class CronAPIThrottle(throttling.UserRateThrottle):
    scope = 'cron'
    cache_format = 'throttle:%(scope)s:%(ident)s'
    
    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = timeparse(period) 
        return (num_requests, duration)

    def debounce_name(self, request):
        str_name = request.get_full_path()
        return str_name
    
    def allow_request(self, request, view):
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        super().get_cache_key(request, view)
        if request.user and request.user.is_authenticated:
            ident = request.user.pk + self.debounce_name(request)
        else:
            ident = self.debounce_name(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


