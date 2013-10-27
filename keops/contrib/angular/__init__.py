
from django.conf import settings
from keops.forms.admin import actions

if not hasattr(settings, 'FORM_RENDER_MODULE'):
    settings.FORM_RENDER_MODULE = 'keops.contrib.angular.render'

# Adjust client-side common admin actions
actions.delete_selected.html = lambda x: '''<li><a style="cursor: pointer;" ng-click="confirmDelete()">%s</a></li>''' % x.short_description
actions.duplicate_selected.html = lambda x: '''<li ng-show="form.item.pk"><a style="cursor: pointer;" ng-click="form.newItem(form.item.pk)">%s</a></li>''' % x.short_description
