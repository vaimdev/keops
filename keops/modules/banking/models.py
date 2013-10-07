from django.utils.translation import ugettext_lazy as _
from keops.db import models
from keops.modules.base import models as base

class Bank(models.Model):
    code = models.CharField(_('Bank Identifier Code'), max_length=64)
    name = models.CharField(_('name'), max_length=128, help_text=_('Bank name'))
    active = models.BooleanField(_('active'), default=True)
    country = models.ForeignKey(base.Country, verbose_name=_('country'))
    email = models.EmailField('e-mail')

    class Meta:
        db_table = 'bank'

    class Extra:
        default_fields = ('code', 'name')
