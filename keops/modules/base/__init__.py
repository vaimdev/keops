from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'Base',
    'description': _('Base module required for all keops based business apps.'),
    'category': _('Basic'),
    'version': '0.4',
    'fixtures': ('data.json.django', 'auth.json.django', 'menu.json.django'),
}
