# coding: utf-8

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

local_data = local()

def get_current_request():
    return getattr(local_data, "request", None)

def get_current_user():
    request = get_current_request()
    if request:
        return getattr(request, "user", None)

class ThreadLocalMiddleware(object):
    def process_request(self, request):
        local_data.request = request
