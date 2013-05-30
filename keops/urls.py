from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/', include('keops.views.urls')),
)

urlpatterns += staticfiles_urlpatterns()
