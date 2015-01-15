from django.utils.translation import ugettext_lazy as _
from django.apps import apps
from keops.apps import AppConfig


class ProjectConfig(AppConfig):
    name = 'keops.modules.project'
    verbose_name = _('Projects')
    description = _('Project module.')
    category = _('Project')
    version = (0, 1)
    dependencies = ['keops.modules.base']
