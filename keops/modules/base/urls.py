from django.conf.urls import patterns, include
from django.contrib.auth.views import password_change

urlpatterns = patterns('keops.modules.base',
    (r'^$', 'views.index'),
    (r'^menu/(\d+)/$', 'views.menu.index'),
    (r'^detail/$', 'views.detail.index'),
    (r'^accounts/password/change/$', password_change, {'template_name': 'keops/registration/password_change_form.html'}),
    #(r'^login$', 'views.login')
)
