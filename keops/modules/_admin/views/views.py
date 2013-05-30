
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from keops.modules.base import models as base

def index(request):
    return HttpResponseRedirect('/admin/menu/%d' % base.Menu.objects.filter(parent=None)[0].pk)

def getdb(request):
    return HttpResponse('get database %s' % request.session.get('orun-db'))

def setdb(request):
    request.session['orun-db'] = request.GET['db']
    print(request.GET)
    return HttpResponse('set database %s' % request.session.get('orun-db'))
