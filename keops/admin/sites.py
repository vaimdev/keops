from functools import update_wrapper
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.db import models


class AdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        from keops.modules.base.models import Menu
        # TODO got last user menu
        return HttpResponseRedirect('/admin/menu/%d' % Menu.objects.only('id').filter(parent=None)[0].pk)

    def menu(self, request, menu_id):
        from keops.modules.base.models import Menu
        if 'action' in request.GET:
            return self.response_action(request)
        elif 'menulist' in request.GET:
            return self.response_menu_list(request)

        return render(request, 'keops/app.html', {
            'app_menu': Menu.objects.filter(parent=None),
            'menu': Menu.objects.get(pk=menu_id),
            'user': request.user  # TODO get current company name
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
            url(r'^logout/$',
                wrap(self.logout),
                name='logout')
        )

        return urlpatterns

site = AdminSite('keops')
