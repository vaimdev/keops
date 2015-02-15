from collections import OrderedDict
from functools import update_wrapper
from django.shortcuts import render
from django.contrib import admin
from django.apps import apps as django_apps
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils import six
from django.apps import apps
from keops.db import models
from keops.db.base import get_model
from . import actions
from .options import ModelAdmin, modeladmin_factory


class AdminSite(admin.AdminSite):
    password_change_template = 'keops/registration/password_change_form.html'
    login_template = 'keops/login.html'
    index_template = 'keops/index.html'

    # Text to put at the end of each page's <title>.
    site_title = 'Keops ERP'

    # Text to put in each page's <h1>.
    site_header = 'Katrid Enterprise Objects'

    index_title = ugettext_lazy('Dashboard')

    def __init__(self, name='admin', app_name='admin'):
        self._registry = {}  # model_class/view_class -> admin_class instance
        self._registry_cache = {}
        self.name = name
        self.app_name = app_name
        self._actions = OrderedDict()
        self._actions['duplicate_selected'] = actions.duplicate_selected
        self._actions['delete_selected'] = actions.delete_selected
        self._global_actions = self._actions.copy()

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                    }
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add', False):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': apps.get_app_config(app_label).verbose_name,
                            'app_label': app_label,
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        context = dict(
            self.each_context(),
            title=self.index_title,
            app_list=app_list,
        )
        context.update(extra_context or {})
        return TemplateResponse(request, self.index_template or
                                'admin/index.html', context,
                                current_app=self.name)

    # CRUD/Ajax
    def db_read(self, request, model):
        model = get_model(model)
        admin = self._registry.get(model)
        return admin.db_read(request)

    def db_list(self, request, model):
        model = get_model(model)
        admin = self._registry.get(model)
        return admin.db_list(request)

    def db_save(self, request, db=None):
        pass

    def db_new(self, request, db=None):
        pass

    def menu(self, request, menu_id):
        """
        Admin site menu view.
        """
        return render(request, 'keops/index.html')

    def login(self, request, extra_context=None, db=None):
        return super(AdminSite, self).login(request, extra_context)

    @never_cache
    def show(self, request, model_admin, view_type=None):
        model = model_admin
        if model:
            model = get_model(model)
            admin = self._registry.get(model)
            if admin:
                view_type = view_type or getattr(admin, 'view_type', 'list')
                return admin.render(request, view_type)
            return admin
        return render(request, 'keops/form.html')

    def register(self, model_or_iterable, admin_class=None, **options):
        # Allow to register more than 1 ModelAdmin per Model
        if not isinstance(model_or_iterable, (tuple, list)):
            model_or_iterable = [model_or_iterable]
        for obj in model_or_iterable:
            if issubclass(obj, ModelAdmin):
                if obj.model in self._registry and not obj in self._registry:
                    obj = obj(obj.model, self)
                    model = obj.model
                    self._registry[obj] = obj
                    self._registry_cache[
                        ('%s.admin.%s' % (model._meta.app_label, model._meta.model_name)).lower()] = obj
            elif issubclass(obj, models.Model):
                admin = modeladmin_factory(obj, **options)(obj, self)
                self._registry[obj] = admin
                self._registry_cache[str(obj._meta).lower()] = admin
            else:
                raise Exception('Invalid model admin class registration')

    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view, cacheable=False):
            return view

            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = patterns('',
           url(r'^$', wrap(self.index), name='index'),
           url(r'^login/$', self.login, name='login'),
           url(r'^menu/(\d+)/$', wrap(self.menu), name='menu'),
           url(r'^show/(\w+\.\w+\.*\w*)/$', wrap(self.show), name='menu'),
           url(r'^show/(\w+\.\w+\.*\w*)/(\w+)/$', wrap(self.show), name='menu'),
           url(r'^db/list/(\w+\.*\w*)/$', wrap(self.db_list), name='db_list'),
           url(r'^db/read/(\w+\.*\w*)/$', wrap(self.db_read), name='db_read'),
           url(r'^logout/$', wrap(self.logout), name='logout'),
           url(r'^password_change/$', wrap(self.password_change, cacheable=True), name='password_change'),
           url(r'^password_change/done/$', wrap(self.password_change_done, cacheable=True), name='password_change_done'),
        )

        return urlpatterns


site = AdminSite('keops')
