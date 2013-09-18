
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from keops.views.decorators import staff_member_required
from keops.modules.base import models as base

#@staff_member_required
def index(request):
    return HttpResponseRedirect('/admin/menu/%d' % base.Menu.objects.filter(parent=None)[0].pk)

def getdb(request):
    return HttpResponse('get database %s' % request.session.get('orun-db'))

def setdb(request):
    request.session['orun-db'] = request.GET['db']
    print(request.GET)
    return HttpResponse('set database %s' % request.session.get('orun-db'))
