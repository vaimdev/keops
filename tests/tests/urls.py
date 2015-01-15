from django.conf.urls import patterns, include, url
from django.contrib import admin
from keops.admin import site

urlpatterns = patterns('',
    url('', include('keops.urls')),
    url(r'^admin/', include(site.urls)),
)
