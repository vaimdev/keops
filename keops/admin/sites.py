from collections import OrderedDict
from functools import update_wrapper
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.db import models
from django.utils.text import capfirst
from . import actions
from .render import render_form


class AdminSite(admin.AdminSite):
    def __init__(self, name='admin', app_name='admin'):
        self._registry = {}  # model_class class -> admin_class instance
        self.name = name
        self.app_name = app_name
        self._actions = OrderedDict()
        self._actions['duplicate_selected'] = actions.duplicate_selected
        self._actions['delete_selected'] = actions.delete_selected
        self._global_actions = self._actions.copy()

    def detail_view(self, request):
        state = request.GET.get('state', 'new')
        model = self.get_model(request.GET['model'])
        field = request.GET.get('field')
        pk = request.GET.get('pk')
        if field:
            field = getattr(model, field)
            related = field.related
            rel_model = related.model
            content = render_form(rel_model._admin, cols=2, exclude=[related.field.name], state='write')
            return render(request, 'keops/forms/detail_dialog.html', {
                'header': capfirst(field.verbose_name or field.name),
                'content': content
            })

    def dispatch_action(self, request):
        """
        Dispatch the admin action.
        """
        from keops.db import get_db
        using = get_db(request)
        model = self.get_model(request.GET['model'])
        admin = model._admin
        pk = request.GET.get('pk')
        action = admin.get_action(request.GET['action'])[0]
        queryset = None
        if pk:
            queryset = model.objects.using(using).filter(pk=pk)
        return action(admin, request, queryset)

    def index(self, request, extra_context=None):
        from keops.modules.base.models import Menu
        # TODO got last user menu
        return HttpResponseRedirect('/admin/menu/%d' % Menu.objects.only('id').filter(parent=None)[0].pk)

    def history(self, request):
        model = self.get_model(request.GET['model'])
        pk = request.GET['pk']
        return model._admin.history_view(request, object_id=pk)

    def menu(self, request, menu_id):
        from keops.modules.base.models import Menu
        if 'action' in request.GET:
            return self.response_action(request)
        elif 'menulist' in request.GET:
            return self.response_menu_list(request)

        return render(request, 'keops/app.html', {
            'app_menu': Menu.objects.filter(parent=None),
            'menu': Menu.objects.get(pk=menu_id),
            'user': request.user,  # TODO get current company name
            'company': request.session['company']
        })

    def response_action(self, request):
        from keops.modules.base.models import Action
        action = Action.objects.get(pk=request.GET.get('action'))
        return action.execute(request, view_type=request.GET.get('view_type'))


    def response_menu_list(self, request):
        from keops.modules.base.models import Menu
        menu = Menu.objects.get(pk=request.GET['menulist'])
        return render(request, 'keops/menu_list.html', {'menu': menu})

    def get_model(self, model_name):
        return models.get_model(*model_name.split('.'))

    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.index),
                name='index'),
            url(r'^menu/(\d+)/$',
                wrap(self.menu),
                name='menu'),
            url(r'^action/$',
                wrap(self.dispatch_action),
                name='action'),
            url(r'^detail/$',
                wrap(self.detail_view),
                name='history'),
            url(r'^history/$',
                wrap(self.history),
                name='history'),
            url(r'^logout/$',
                wrap(self.logout),
                name='logout')
        )

        return urlpatterns

site = AdminSite('keops')
