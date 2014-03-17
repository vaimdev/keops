import re
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import models as auth
from django.contrib.auth.models import Group
import django.contrib.auth.signals
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import validators
from django.utils import timezone
from django.contrib.admin.util import quote
from django.utils.encoding import smart_text
from django.core.mail import send_mail
from keops.db import models
from .element import ElementManager


Group.add_to_class('module_category', models.ForeignKey('base.modulecategory', verbose_name=_('category')))


class CompanyManager(ElementManager):
    def get_queryset(self):
        return super(CompanyManager, self).get_queryset().defer('image')  # default defer image


# Company/data context
class Company(models.Model):
    """
    Company configuration model.
    """
    parent_company = models.ForeignKey('self')
    name = models.CharField(_('name'), max_length=100, null=False)
    logo = models.ImageField('logo')
    currency = models.ForeignKey('base.currency', verbose_name=_('currency'))
    report_style = models.CharField(_('report style'), max_length=64, page=_('Report Configurations'))
    report_header = models.TextField(_('report header'), page=_('Report Configurations'))
    report_footer = models.TextField(_('report footer'), page=_('Report Configurations'))

    objects = CompanyManager()

    class Meta:
        db_table = 'base_company'
        verbose_name = _('company')
        verbose_name_plural = _('companies')

        class Admin:
            display_expression = ('name',)
            field_groups = {
                'list_fields': ('name', 'country', 'website'),
                'search_fields': ('name', 'country', 'website'),
            }


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
    company = models.ForeignKey('base.company', default=False)
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

    is_company = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)

    objects = ContactManager()

    class Meta:
        db_table = 'base_contact'
        verbose_name = _('contact')

    def email_contact(self, subject, message, from_email=None):
        """
        Sends an email to this Contact.
        """
        send_mail(subject, message, from_email, [self.email])


class User(auth.AbstractUser):
    contact = models.ForeignKey(Contact)
    email_signature = models.TextField(_('e-mail signature'))
    document_signature = models.TextField(_('document signature'))
    company = models.ForeignKey('base.company', verbose_name=_('company'), help_text=_('default user company'), related_name='+')
    companies = models.ManyToManyField('base.company', verbose_name=_('allowed companies'), help_text=_('user allowed companies'))
    status = models.CharField(max_length=16, choices=(('created', _('Created')), ('activated', _('activated'))), visible=False)

    raw_password = property(fset=auth.AbstractUser.set_password)

    REQUIRED_FIELDS = ['email', 'username']

    class Meta:
        db_table = 'auth_user'

        class Admin:
            field_groups = {
                'list_fields': ('username', 'name', 'email'),
                'search_fields': ('username', 'name', 'email'),
            }

    def __str__(self):
        return self.username + self.get_full_name()

    def get(self, key, default=None):
        """
        Return user data value.
        """
        data = UserData.objects.using(self._state.db).filter(user=self, key=key)
        if data:
            return data[0].value
        else:
            return default

    def set(self, key, value):
        """
        Set user data value.
        """
        db = self._state.db
        data = UserData.objects.using(db).filter(user=self, key=key)
        if data:
            data = data[0]
        else:
            data = UserData(user=self, key=key)
        data.value = value
        data.save(using=db)

    def setdefault(self, key, default):
        """
        Set user data default value.
        """
        db = self._state.db
        data = UserData.objects.using(db).filter(user=self, key=key)
        if data:
            return data[0].value
        UserData.objects.using(db).create(user=self, key=key, value=default)
        return default


class UserContent(models.Model):
    """
    User/author content object log.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), null=False, related_name='+')
    object_id = models.PositiveIntegerField(_('object id'), null=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('created by'), null=False, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'), null=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('modified by'), related_name='+')
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_('modified on'))

    class Meta:
        db_table = 'auth_user_content'


class UserData(models.Model):
    """
    User profile data.
    """
    user = models.ForeignKey(User, null=False)
    key = models.CharField(max_length=64, db_index=True)
    value = models.TextField()

    class Meta:
        unique_together = (('user', 'key'),)
        db_table = 'auth_user_data'
