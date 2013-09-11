from django.db import DEFAULT_DB_ALIAS
from threading import local

SESSION_DB_KEY = '_db_alias'

local_data = local()

def get_current_request():
    return getattr(local_data, "request", None)

def get_current_user():
    request = get_current_request()
    if request:
        return getattr(request, "user", None)

def get_db(request=None):
    if not request:
        request = get_current_request()
    if request:
        return request.session.setdefault(SESSION_DB_KEY, DEFAULT_DB_ALIAS)

def set_db(alias, request=None):
    if not request:
        request = get_current_request()
    if request:
        request.session[SESSION_DB_KEY] = alias

class ThreadLocalMiddleware(object):
    def process_request(self, request):
        local_data.request = request
