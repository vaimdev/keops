from functools import wraps
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def staff_member_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, displaying the login page if necessary.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            # The user is valid. Continue to the admin page.
            return view_func(request, *args, **kwargs)

        return HttpResponseRedirect(settings.LOGIN_URL + '?next=/admin/')
    return _checklogin
