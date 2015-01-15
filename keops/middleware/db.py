from django.conf import settings
from django.core.urlresolvers import resolve
from django.db import DEFAULT_DB_ALIAS, connections
from django.utils.functional import SimpleLazyObject
from threading import local

MULTI_DB = ('keops.middleware.db.PathMiddleware' in settings.MIDDLEWARE_CLASSES) or \
           ('keops.middleware.db.SubdomainMiddleware' in settings.MIDDLEWARE_CLASSES)

if MULTI_DB:
    SESSION_DB_KEY = '_keops_db_%s'
else:
    SESSION_DB_KEY = '_keops_db'

local_data = local()


def get_request():
    return getattr(local_data, 'request', None)


def get_user():
    request = get_request()
    if request:
        return getattr(request, 'user', None)


def get_db(request=None):
    if not request:
        request = get_request()
    if MULTI_DB:
        if 'keops.middleware.db.PathMiddleware' in settings.MIDDLEWARE_CLASSES:
            return resolve(request.path).kwargs.get('db')
        else:
            return resolve(request.path).kwargs.get('db')
    else:
        return request.session.setdefault(SESSION_DB_KEY, DEFAULT_DB_ALIAS)


def get_connection(request=None):
    return connections[get_db(request)]


def set_db(alias, request=None):
    if not request:
        request = get_request()
    if request:
        request.session[SESSION_DB_KEY] = alias


class SingleDatabaseMiddleware(object):
    def process_request(self, request):
        local_data.request = request
        request.db = get_db(request)
        request.connection = SimpleLazyObject(lambda: get_connection(request))


class MultiDatabaseMiddleware(SingleDatabaseMiddleware):
    pass


class PathMiddleware(MultiDatabaseMiddleware):
    pass


class SubdomainMiddleware(MultiDatabaseMiddleware):
    pass
