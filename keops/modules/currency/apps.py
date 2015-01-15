from django.utils.translation import ugettext_lazy as _
from keops.apps import AppConfig


class CurrencyConfig(AppConfig):
    version = '0.1'
    verbose_name = 'Currency'
    description = _('Currency integration module')
    category = _('Business')
    requirements = ['keops.modules.internationalization']
