from keops.forms.admin import site


def action(request):
    return site.dispatch_action(request)
