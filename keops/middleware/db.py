import builtins
from django.conf import settings
from django.core.urlresolvers import resolve
from django.db import DEFAULT_DB_ALIAS, connections
from django.utils.functional import SimpleLazyObject
from threading import local

MULTI_DB = 'keops.middleware.db.MultiDBMiddleware' in settings.MIDDLEWARE_CLASSES

if MULTI_DB:
    SESSION_DB_KEY = '_keops_db_%s'
else:
    SESSION_DB_KEY = '_keops_db'

local_data = local()


def current_request():
    return getattr(local_data, "request", None)


def current_user():
    request = current_request()
    if request:
        return getattr(request, "user", None)


def get_db(request=None):
    if not request:
        request = current_request()
    if MULTI_DB:
        return resolve(request.path).kwargs.get('db')
    else:
        return request.session.setdefault(SESSION_DB_KEY, DEFAULT_DB_ALIAS)


def get_connection(request=None):
    return connections[get_db(request)]


def set_db(alias, request=None):
    if not request:
        request = current_request()
    if request:
        request.session[SESSION_DB_KEY] = alias


class SingleDBMiddleware(object):
    def process_request(self, request):
        local_data.request = request
        request.db = get_db(request)
        request.connection = SimpleLazyObject(lambda: get_connection(request))


class MultiDBMiddleware(SingleDBMiddleware):
    pass
