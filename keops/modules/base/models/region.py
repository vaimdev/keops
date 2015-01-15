from django.utils.translation import ugettext_lazy as _
from keops.db import models


class Country(models.Model):
    name = models.CharField(_('name'), max_length=64, unique=True)
    code = models.CharField(_('country code'), max_length=2, help_text='The ISO country code')
    phone_code = models.CharField(_('phone code'), max_length=10)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class State(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('country'), null=False)
    code = models.CharField(_('state code'), max_length=3, null=False, db_index=True)
    name = models.CharField(_('name'), max_length=64, null=False, db_index=True)

    class Meta:
        db_table = 'base_state'
        unique_together = (('country', 'code'), ('country', 'name'))
        verbose_name = _('state')
        ordering = ('name',)
