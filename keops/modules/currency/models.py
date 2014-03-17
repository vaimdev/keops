from django.utils.translation import ugettext_lazy as _
from keops.db import models
from keops.modules.base import models as base


class CurrencyRateType(models.Model):
    name = models.CharField(_('name'), max_length=64)

    class Meta:
        db_table = 'base_currency_rate_type'
        verbose_name = _('currency rate type')


class CurrencyRate(models.Model):
    date = models.DateField(_('date'))
    currency = models.ForeignKey(base.Currency, verbose_name=_('currency'))
    currency_rate_type = models.ForeignKey(CurrencyRateType, verbose_name=_('rate type'))
    rate = models.MoneyField(_('rate'))

    class Meta:
        db_table = 'base_currency_rate'
