from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url

js_info_dict = {
    'packages': ('keops',),
}

urlpatterns = patterns('',
    url(r'^(?P<db>\w+)/db/read/$', 'keops.views.db.read', name='db_read'),
    (r'^jsi18n/', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns += staticfiles_urlpatterns()
