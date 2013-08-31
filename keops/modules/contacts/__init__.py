
from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'contacts',
    'description': _('Base module'),
    'category': _('Base'),
    'version': '0.1',
    'fixtures': ('data.json', 'auth.json'),
}
