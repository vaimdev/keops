from . import settings

settings.BASE_APPS = settings.INSTALLED_APPS[:]


class Context(object):
    @property
    def request(self):
        from keops.middleware.threadlocal import get_current_request
        return get_current_request()

    @property
    def session(self):
        return self.request.session

    @property
    def db(self):
        from keops.middleware.threadlocal import get_db
        return get_db()

    def get_db(self, request):
        from keops.middleware.threadlocal import get_db
        return get_db(request)

context = Context()
