# coding: utf-8
from django.db import DEFAULT_DB_ALIAS
from threading import local

local_data = local()

def get_current_request():
    return getattr(local_data, "request", None)

def get_current_user():
    request = get_current_request()
    if request:
        return getattr(request, "user", None)

def get_db():
    request = get_current_request()
    if request:
        return request.session.setdefault('_db_alias', DEFAULT_DB_ALIAS)

def set_db(alias):
    request = get_current_request()
    if request:
        request.session['_db_alias'] = alias

class ThreadLocalMiddleware(object):
    def process_request(self, request):
        local_data.request = request
