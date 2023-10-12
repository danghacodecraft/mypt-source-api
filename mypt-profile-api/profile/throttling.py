import json
from rest_framework.throttling import UserRateThrottle


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

