
from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'base',
    'description': _('Base module'),
    'category': _('Base'),
    'version': '0.3',
    'fixtures': ('data.json', 'auth.json'),
}
