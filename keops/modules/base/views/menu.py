
import json
from django.shortcuts import render
from django.http import HttpResponse
from keops.modules.base import models as base
from keops import forms

def index(request, menu_id):
    
    if 'action' in request.GET:
        return response_action(request)

    menu = base.Menu.objects.filter(parent_id=menu_id)

    def get_sub_menu(item):
        return [{'text': m.name, 'leaf': m.menu_set.count() == 0, 'children': get_sub_menu(m), 'href': '#action=%d' % m.action.pk if m.action else '#'} for m in base.Menu.objects.filter(parent_id=item.pk)]
    
    sub_menu = json.dumps([{
        'xtype': 'treemenu',
        'rootVisible': False,
        'title': m.name,
        'lines': False,
        'useArrows': True,
        'root': {'expanded': True, 'children': get_sub_menu(m)}} for m in menu])
    
    return render(request, 'keops/app.html', {'main_menu': base.Menu.objects.filter(parent=None), 
        'sub_menu': sub_menu,
        'menu': base.Menu.objects.get(pk=menu_id),
        'site_name': 'PREFEITURA MUNICIPAL DE MODELO'})

def response_action(request):
    from keops.modules.base.models import Action
    action = Action.objects.get(pk=request.GET.get('action'))
    return action.execute(request)
