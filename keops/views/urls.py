from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    (r'^', include('keops.modules.base.urls')),
    (r'^db/grid/$', 'keops.views.db.grid'),
    (r'^db/read/$', 'keops.views.db.read'),
    (r'^db/lookup/$', 'keops.views.db.lookup'),
    (r'^db/submit/$', 'keops.views.db.submit'),
    (r'^test/$', 'keops.views.test.index'),
)

urlpatterns += staticfiles_urlpatterns()
