from django.conf.urls import patterns, include

urlpatterns = patterns('keops.contrib.datapages',
    (r'^$', 'views.index'),
)
