from django.conf import settings
from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from keops import forms

js_info_dict = {
    'packages': ('keops',),
}

urlpatterns = patterns('',
    # db
    (r'^db/grid/$', 'keops.views.db.grid'),
    (r'^db/read/$', 'keops.views.db.read'),
    (r'^db/read/items/$', 'keops.views.db.read_items'),
    (r'^db/lookup/$', 'keops.views.db.lookup'),
    (r'^db/submit/$', 'keops.views.db.submit'),
    (r'^db/new/$', 'keops.views.db.new_item'),
    (r'^db/field/change$', 'keops.views.db.field_change'),
    (r'^db/test/$', 'keops.views.test.index'),
    # additional
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/', include('keops.modules.base.urls')),
    (r'^jsi18n/', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns += staticfiles_urlpatterns()

# Autodiscover apps forms
forms.autodiscover()
