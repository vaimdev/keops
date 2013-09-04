from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from keops import forms

urlpatterns = patterns('',
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/', include('keops.views.urls')),
)

urlpatterns += staticfiles_urlpatterns()

# Autodiscover apps forms
forms.autodiscover()
