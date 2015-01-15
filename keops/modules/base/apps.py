from django.utils.translation import ugettext_lazy as _
from keops.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'keops.modules.base'
    verbose_name = _('Base')
    description = _('Base module required for all keops based apps.')
    category = _('Basic')
    version = (0, 4)
    fixtures = ['company.json', 'data.json.django', 'auth.json.django', 'menu.json.django']
