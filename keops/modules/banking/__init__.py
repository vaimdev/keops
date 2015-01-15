from django.utils.translation import ugettext_lazy as _
from keops.apps import AppConfig


class BankingConfig(AppConfig):
    name = 'keops.modules.banking'
    description = _('Basic banking module.')
    category = _('Banking')
    version = (0, 1)
    dependencies = ['keops.modules.base']
