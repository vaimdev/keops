from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from keops import forms

js_info_dict = {
    'packages': ('keops',),
}

urlpatterns = patterns('',
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/', include('keops.views.urls')),
    (r'^jsi18n/', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns += staticfiles_urlpatterns()

# Autodiscover apps forms
forms.autodiscover()
