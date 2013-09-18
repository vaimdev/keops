import json
from django.shortcuts import render
from django.http import HttpResponse
from keops.modules.base import models as base
from keops import forms

def index(request, menu_id):
    if 'action' in request.GET:
        return response_action(request)

    return render(request, 'keops/app.html', {
        'app_menu': base.Menu.objects.filter(parent=None),
        'menu': base.Menu.objects.get(pk=menu_id),
        'site_name': 'COMPANY NAME'
    })

def response_action(request):
    from keops.modules.base.models import Action
    action = Action.objects.get(pk=request.GET.get('action'))
    return action.execute(request)
