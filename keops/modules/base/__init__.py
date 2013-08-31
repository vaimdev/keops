
from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'base',
    'description': _('Base module required for all keops based business apps.'),
    'category': _('Hidden'),
    'version': '0.3',
    'fixtures': ('data.json', 'auth.json'),
}
