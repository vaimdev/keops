from django.utils.translation import ugettext_lazy as _
from keops.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'keops.modules.product'
    verbose_name = _('Products')
    description = _('Basic product module implementation.')
    category = _('Warehouse')
    version = (0, 1)
