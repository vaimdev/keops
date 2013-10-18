from django.conf.urls import patterns, include

urlpatterns = patterns('keops.modules.base',
    (r'^$', 'views.index'),
    (r'^menu/(\d+)/$', 'views.menu.index'),
    (r'^detail/$', 'views.detail.index'),
    #(r'^login$', 'views.login')
)
