from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from keops.db import models


class Config(models.Model):
    account_mask = models.CharField(_('account mask'))


class AccountType(models.Model):
    name = models.CharField(max_length=32, null=False, db_index=True)

    class Meta:
        db_table = 'account_type'


class FiscalYear(models.Model):
    STATUS = (
        ('opened', _('Opened')),
        ('closed', _('Closed'))
    )
    code = models.CharField(_('code'), max_length=24, null=False)
    name = models.CharField(max_length=32, null=False)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    status = models.CharField(max_length=8, choices=STATUS, readonly=True)


class FiscalPeriod(models.Model):
    fiscal_year = models.ForeignKey(FiscalYear, null=False)
    code = models.CharField(_('code'), max_length=24, null=False, db_index=True)
    name = models.CharField(_('period name'), max_length=32, null=False)
    start_period = models.DateField(_('start date'))
    end_period = models.DateField(_('end date'))
    status = models.CharField(max_length=8, choices=FiscalYear.STATUS, readonly=True)


class Account(models.Model):
    #code = models.CharField(_('code'), max_length=32, help_text=_('Account code'), null=False, db_index=True, custom_attrs={'mask': AccountConfig.account_mask})
    name = models.CharField(_('name'), max_length=64, help_text=_('Account name'), null=False, db_index=True)
    parent = models.ForeignKey('self', verbose_name=_('Parent'), help_text=_('Parent account'))
    active = models.BooleanField()
    account_type = models.ForeignKey(AccountType, verbose_name=_('account type'))
    notes = models.TextField(_('notes'))

    class Meta:
        db_table = 'account'


class BankType(models.Model):
    name = models.CharField(_('name'), max_length=32, db_index=True)

    class Meta:
        db_table = 'account_bank_type'


class BankAccount(models.Model):
    account = models.ForeignKey(Account, verbose_name=_('account'))
    account_type = models.ForeignKey(BankType)
    number = models.CharField(_('number'), help_text=_('Account number'), null=False)


class Move(models.Model):
    fiscal_period = models.ForeignKey(FiscalPeriod, null=False, on_delete=models.CASCADE)
    description = models.CharField(_('description'), max_length=128, null=False)
    move_date = models.DateField(_('date'), null=False, db_index=True)
    debit = models.MoneyField(_('debit'), default=0, readonly=True)
    credit = models.MoneyField(_('credit'), default=0, readonly=True)
    balance = models.MoneyField(_('balance'), default=0, readonly=True)

    def __str__(self):
        return '%s - %s' % (str(self.id), self.description)

    class Meta:
        db_table = 'account_move'

    class Extra:
        default_fields = ('id', 'description')


class MoveLine(models.Model):
    account_move = models.ForeignKey(Move, null=False)
    document = models.CharField(max_length=32, db_index=True)
    debit_account = models.ForeignKey(Account, verbose_name='debit account', related_name='+')
    credit_account = models.ForeignKey(Account, verbose_name='credit account', related_name='+')
    value = models.MoneyField(blank=False)
    debit = models.MoneyField(default=0)
    credit = models.MoneyField(default=0)
    notes = models.TextField(_('notes'))

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'account_move_line'

    class Extra:
        default_fields = ('id',)
