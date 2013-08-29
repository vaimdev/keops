from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from keops.db import models
from keops.modules.base import models as base

class Currency(models.Model):
    name = models.CharField(_('name'), max_length=32, null=False, unique=True)
    symbol = models.CharField(_('currency symbol'), max_length=10, null=False)
    rounding = models.MoneyField(_('rounding'), default=0.01)
    active = models.BooleanField(_('active'))
    display_format = models.CharField(_('display format'), max_length=16)
    
class CurrencyRateType(models.Model):
    name = models.CharField(_('name'), max_length=64)
    
    class Meta:
        db_table = 'base_currency_rate_type'
        verbose_name = _('currency rate type')
        
class CurrencyRate(models.Model):
    date = models.DateField(_('date'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))
    currency_rate_type = models.ForeignKey(CurrencyRateType, verbose_name=_('rate type'))
    rate = models.MoneyField(_('rate'))
    
    class Meta:
        db_table = 'base_currency_rate'

class Language(models.Model):
    code = models.CharField(_('code'), max_length=5)
    iso_code = models.CharField(_('ISO code'), max_length=10)
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))
    translate = models.BooleanField(_('translate'), default=False)
    
    class Meta:
        verbose_name = _('language')

class Translation(models.Model):
    """
    Translates database field value.
    """
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(_('name'), max_length=64)
    language = models.ForeignKey(Language, verbose_name=_('language'))
    source = models.TextField(_('source'), db_index=True)
    value = models.TextField(_('value'))
    
    class Meta:
        unique_together = (('content_type', 'name'))
        verbose_name = _('translation')
        verbose_name_plural = _('translations')
        
class Country(models.Model):
    name = models.CharField(_('name'), max_length=64, unique=True)
    code = models.CharField(_('web code'), max_length=2)
    language = models.ForeignKey(Language, verbose_name=_('language'))
    phone_code = models.CharField(_('phone code'), max_length=10)
    
    class Meta:
        verbose_name = _('country')

class Company(base.Element):
    parent = models.ForeignKey('self')
    report_header = models.TextField(_('report header'))
    report_footer = models.TextField(_('report footer'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))
    country = models.ForeignKey(Country)
    #logo = models.ImageField(_('Logo'))
    email = models.EmailField('e-mail')
    phone = models.CharField(_('phone'), max_length=32)
    fax = models.CharField(_('fax'), max_length=32)
    web_site = models.URLField('web site')
    info = models.TextField(_('information'), help_text='Additional information')

class State(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('country'), null=False)
    code = models.CharField(_('code'), max_length=3, null=False)
    name = models.CharField(_('name'), max_length=64, null=False)
    
    class Meta:
        db_table = 'base_state'
        unique_together = (('country', 'code'), ('country', 'name'))
        verbose_name = _('state')
