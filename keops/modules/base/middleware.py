from django.utils.functional import SimpleLazyObject


def get_user(request):
    if not hasattr(request, '_cached_company'):
        request._cached_company = request.user.default_company
    return request._cached_company


class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Keops authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.company = SimpleLazyObject(lambda: get_user(request))

