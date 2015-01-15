from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from keops.db import models
from keops.modules.base import models as base


class Translation(models.Model):
    """
    Translates database field value.
    """
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(_('name'), max_length=64)
    language = models.ForeignKey('language', verbose_name=_('language'))
    source = models.CharField(_('source'), max_length=1024, db_index=True)
    value = models.TextField(_('value'))

    class Meta:
        unique_together = (('content_type', 'name'),)
        verbose_name = _('translation')
        verbose_name_plural = _('translations')


class Contact(base.Contact):
    time_zone = models.CharField(_('time zone'), max_length=32)
    language = models.ForeignKey('base.language')

    class Meta:
        proxy = True


class Company(base.Company):
    currency = models.ForeignKey('currency', verbose_name=_('currency'))

    class Meta:
        proxy = True


class Currency(models.Model):
    name = models.CharField(_('name'), max_length=32, null=False, unique=True)
    symbol = models.CharField(_('symbol'), max_length=10, null=False)
    rounding = models.MoneyField(_('rounding'), default=0.01)
    active = models.BooleanField(_('active'), default=True)
    display_format = models.CharField(_('display format'), max_length=16)


class Language(models.Model):
    code = models.CharField(_('locale code'), max_length=5, null=False, unique=True)
    name = models.CharField(_('name'), max_length=64, null=False, unique=True)
    iso_code = models.CharField(_('ISO code'), max_length=10)
    translate = models.BooleanField(_('translate'), default=False)
    active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('language')


class Country(base.Country):
    language = models.ForeignKey(Language, verbose_name=_('language'))

    class Meta:
        proxy = True
