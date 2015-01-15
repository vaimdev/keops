import json
from functools import update_wrapper
from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from keops.admin import sites as admin


class AdminSite(admin.AdminSite):
    def menu(self, request, menu_id):
        """
        Load menu structure from Menu database model.
        """
        from keops.modules.base.models import Menu
        if 'action' in request.GET:
            return self.response_action(request)
        elif 'menulist' in request.GET:
            return self.response_menu_list(request)

        return render(request, 'keops/index.html', {
            'app_menu': Menu.objects.filter(parent=None),
            'menu': Menu.objects.get(pk=menu_id),
        })

    def index(self, request, db=None, extra_context=None):
        from keops.modules.base.models import Menu
        # TODO got last user menu
        return HttpResponseRedirect('/admin/menu/%d' % Menu.objects.only('id').filter(parent=None)[0].pk)

    def response_menu_list(self, request):
        from keops.modules.base.models import Menu
        menu = Menu.objects.get(pk=request.GET['menulist'])
        return render(request, 'keops/menu_list.html', {'menu': menu})

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
        if request.body:
            data = json.loads(request.body.decode(settings.DEFAULT_CHARSET))
            request.POST = data
        else:
            data = request.GET
        model = self.get_model(data['model'])
        admin = model._admin
        pk = request.GET.get('pk')
        action = admin.get_action(data['action'])[0]
        queryset = None
        if pk:
            queryset = model.objects.using(using).filter(pk=pk)
        return action(admin, request, queryset)

    def admin_view(self, view, cacheable=False):
        """
        Decorator to create an admin view attached to this ``AdminSite``. This
        wraps the view and provides permission checking by calling
        ``self.has_permission``.

        You'll want to use this from within ``AdminSite.get_urls()``:

            class MyAdminSite(AdminSite):

                def get_urls(self):
                    from django.conf.urls import patterns, url

                    urls = super(MyAdminSite, self).get_urls()
                    urls += patterns('',
                        url(r'^my_view/$', self.admin_view(some_view))
                    )
                    return urls

        By default, admin_views are marked non-cacheable using the
        ``never_cache`` decorator. If the view can be safely cached, set
        cacheable=True.
        """
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.path == reverse('admin:logout', kwargs={'db': kwargs['db']}, current_app=self.name):
                    index_path = reverse('admin:index', kwargs={'db': kwargs['db']}, current_app=self.name)
                    return HttpResponseRedirect(index_path)
                # Inner import to prevent django.contrib.admin (app) from
                # importing django.contrib.auth.models.User (unrelated model).
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    request.get_full_path(),
                    reverse('admin:login', kwargs={'db': kwargs['db']}, current_app=self.name)
                )
            return view(request, *args, **kwargs)
        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view, cacheable=False):
            return view
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        # Admin-site-wide views with DB URL parameter.
        urlpatterns = patterns('',
            url(r'^(?P<db>\w+)/login/$',
                self.login,
                name='login'),
            url(r'^(?P<db>\w+)/$',
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
                name='detail'),
            url(r'^history/$',
                wrap(self.history),
                name='history'),
            url(r'^(?P<db>\w+)/logout/$',
                wrap(self.logout),
                name='logout'),
            url(r'^password_change/$',
                wrap(self.password_change, cacheable=True),
                name='password_change'),
            url(r'^password_change/done/$',
                wrap(self.password_change_done, cacheable=True),
                name='password_change_done'),

            # CRUD
            url(r'^(?P<db>\w+)/db/read/$',
                self.db_read,
                name='db_read'),
        )

        return urlpatterns

site = AdminSite()
