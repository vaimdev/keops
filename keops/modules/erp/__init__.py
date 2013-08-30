
from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'erp',
    'description': _('ERP base module'),
    'category': 'Business',
    'dependencies': ['keops.modules.base', 'keops.modules.communication'],
    'version': '0.1',
}
