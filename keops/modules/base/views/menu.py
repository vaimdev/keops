from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from keops.modules.base import models as base
from keops import forms


@login_required
def index(request, menu_id):
    if 'action' in request.GET:
        return response_action(request)
    elif 'menulist' in request.GET:
        return response_menu_list(request)

    return render(request, 'keops/app.html', {
        'app_menu': base.Menu.objects.filter(parent=None),
        'menu': base.Menu.objects.get(pk=menu_id),
        'user': request.user  # TODO get current company name
    })


def response_action(request):
    from keops.modules.base.models import Action
    action = Action.objects.get(pk=request.GET.get('action'))
    return action.execute(request, view_type=request.GET.get('view_type'))


def response_menu_list(request):
    from keops.modules.base.models import Menu
    menu = Menu.objects.get(pk=request.GET['menulist'])
    return render(request, 'keops/menu_list.html', {'menu': menu})
