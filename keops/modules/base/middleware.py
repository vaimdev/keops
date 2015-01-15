from django.utils.functional import SimpleLazyObject


SESSION_DATA_CONTEXT_KEY = '_keops_data_context'


def get_data_context(request=None):
    if request is None:
        from keops.middleware.db import get_request
        request = get_request()
    ctx = request.session[SESSION_DATA_CONTEXT_KEY]
    if not ctx:
        ctx = request.user.default_company_id
        request._cached_data_context = ctx
        request.session[SESSION_DATA_CONTEXT_KEY] = ctx
    return request._cached_data_context


class DataContextMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), \
            "The Keops authentication middleware requires session middleware to be installed. " \
            "Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.data_context = SimpleLazyObject(lambda: get_data_context(request))

