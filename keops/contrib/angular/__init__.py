from django.conf import settings

if not hasattr(settings, 'FORM_RENDER_MODULE'):
    settings.FORM_RENDER_MODULE = 'keops.contrib.angular.render'
