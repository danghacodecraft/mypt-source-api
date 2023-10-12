from pytimeparse.timeparse import timeparse
from rest_framework import throttling


class ExtendedRateThrottle(throttling.UserRateThrottle):
    scope = 'user'

    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = timeparse(period)
        return (num_requests, duration)

    def debounce_name(self, request):
        str_name = request.get_full_path()
        str_name = str_name.split("/")[-1]
        return str_name

    def allow_request(self, request, view):
        if request.method == 'GET':
            return True

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        super().get_cache_key(request, view)
        if request.user and request.user.is_authenticated:
            ident = request.user.pk + self.debounce_name(request)
        else:
            ident = self.get_ident(request) + self.debounce_name(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
