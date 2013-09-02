
from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'ERP',
    'short_description': _('ERP integration module'),
    'description': _('ERP integration module'),
    'category': _('Business'),
    'dependencies': ['keops.modules.communication'],
    'version': '0.1',
}
