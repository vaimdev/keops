from django.utils.translation import ugettext, ugettext_lazy as _
from keops.db import models


class Category(models.Model):
    name = models.CharField(_('name'), max_length=64, help_text=_('Category name'))
    active = models.BooleanField(_('active'), default=True)
    parent = models.ForeignKey('self', verbose_name=_('parent category'))

    class Meta:
        db_table = 'base_contact_category'
        verbose_name = _('Contact Category')
        verbose_name_plural = _('Contact Categories')


class ContactManager(models.Manager):
    def get_queryset(self):
        return super(ContactManager, self).get_queryset().defer('image')  # default defer image


class Contact(models.Model):
    name = models.CharField(_('name'), max_length=128, null=False)
    image = models.ImageField(verbose_name=_('image'))
    active = models.BooleanField(_('active'), default=True)
    parent = models.ForeignKey('self')
    category = models.ForeignKey(Category, verbose_name=_('Contact Category'))
    language = models.ForeignKey('base.language')
    time_zone = models.CharField(_('time zone'), max_length=32)
    comments = models.TextField(_('comments'))
    address = models.CharField(_('address'), max_length=256)
    city = models.CharField(_('city'), max_length=64)
    zip_code = models.CharField(_('zip'), max_length=32)
    country = models.ForeignKey('base.country', verbose_name=_('country'))
    email = models.EmailField('email', unique=True)
    website = models.URLField('website')
    phone = models.CharField(_('phone'), max_length=64)
    fax = models.CharField(_('fax'), max_length=64)
    mobile = models.CharField(_('mobile'), max_length=64)
    birthdate = models.DateField(_('birthdate'))
    use_company_address = models.BooleanField(_('use company address'), default=False)

    objects = ContactManager()

    class Meta:
        db_table = 'base_contact'
        verbose_name = _('contact')



