
from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'Contacts',
    'short_description': _('Address Book, Contacts, Partners'),
    'description': _('Address Book, Contacts, Partners'),
    'category': _('Communication'),
    'version': '0.1',
    'fixtures': ('data.json', 'auth.json'),
}
