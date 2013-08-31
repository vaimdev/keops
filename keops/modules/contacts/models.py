
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from keops.modules.base import models as base

class Category(models.Model):
    name = models.CharField(_('name'), max_length=64, help_text=_('Category name'))
    active = models.BooleanField(_('active'), default=True)
    parent = models.ForeignKey('self', verbose_name=_('parent category'))

    class Meta:
        db_table = 'contact_category'

class Contact(base.CompanyModel):
    name = models.CharField(_('name'), max_length=128, null=False)
    #image
    active = models.BooleanField(_('active'), default=True)
    parent_id = models.ForeignKey('self')
    partner_category = models.ForeignKey(Category, verbose_name=_('partner category'))
    language = models.ForeignKey('base.Language')
    time_zone = models.CharField(_('time zone'), max_length=32)
    comment = models.TextField(_('comments'))
    is_customer = models.BooleanField(_('is customer'), default=False)
    is_supplier = models.BooleanField(_('is supplier'), default=False)
    is_employee = models.BooleanField(_('is employee'), default=False)
    is_company = models.BooleanField(_('is company'), default=False)
    address = models.CharField(_('address'), max_length=256)
    country = models.ForeignKey('base.Country', verbose_name=_('country'))
    email = models.EmailField('e-mail')
    website = models.URLField('website')
    phone = models.CharField(_('phone'), max_length=64)
    phone = models.CharField(_('fax'), max_length=64)
    mobile = models.CharField(_('mobile'), max_length=64)
    birthdate = models.DateField(_('birthdate'))
    use_company_address = models.BooleanField(_('use company address'), default=False)

    class Meta:
        db_table = 'contact'
