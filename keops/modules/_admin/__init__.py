
from django.utils.translation import ugettext_lazy as _

__info__ = {
    'name': 'admin',
    'description': _('Basic admin module'),
    'category': _('Base'),
    'version': '0.1',
    'fixtures': ('data.json',),
    'dependencies': ('keops.modules.base', )
}
