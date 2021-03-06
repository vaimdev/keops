from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import models as auth
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.mail import send_mail
from keops.db import models
from .element import ElementManager


Group.add_to_class('module_category', models.ForeignKey('base.modulecategory', verbose_name=_('category')))


class CompanyManager(models.Manager):
    def filter_by_user(self, user, **kwargs):
        return self.filter(**kwargs)


# Company/Data Context
class Company(models.Model):
    """
    Company/Data Context configuration model.
    """
    parent_company = models.ForeignKey('self')
    name = models.CharField(_('name'), max_length=100, null=False)
    logo = models.ImageField('logo')
    report_style = models.CharField(_('report style'), max_length=64, page=_('Report Configurations'))
    report_header = models.TextField(_('report header'), page=_('Report Configurations'))
    report_footer = models.TextField(_('report footer'), page=_('Report Configurations'))
    allow_login = models.BooleanField(default=True)

    objects = CompanyManager()

    class Meta:
        db_table = 'base_company'
        verbose_name = _('company')
        verbose_name_plural = _('companies')

        class Admin:
            display_expression = ('name',)
            list_fields = ('name', 'country', 'website')
            search_fields = ('name', 'country', 'website')


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

    is_company = models.BooleanField(default=False, db_index=True)
    is_employee = models.BooleanField(default=False, db_index=True)
    is_supplier = models.BooleanField(default=False, db_index=True)

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
    STATUS = (
        ('created', _('Created')),
        ('activated', _('Activated')),
        ('blocked', _('Blocked')),
    )
    contact = models.ForeignKey(Contact)  # Related contact
    email_signature = models.TextField(_('e-mail signature'))
    document_signature = models.TextField(_('document signature'))
    company = models.ForeignKey('base.company', verbose_name=_('company'), help_text=_('default user company'), related_name='+')
    companies = models.ManyToManyField('base.company', verbose_name=_('allowed companies'), help_text=_('user allowed companies'))
    status = models.CharField(max_length=16, choices=STATUS, visible=False)

    raw_password = property(fset=auth.AbstractUser.set_password)

    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'auth_user'

        class Admin:
            list_fields = ('username', 'name', 'email')
            search_fields = ('username', 'name', 'email')

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


class UserData(models.Model):
    """
    User profile data.
    """
    user = models.ForeignKey(User, null=False)
    key = models.CharField(max_length=256, db_index=True)
    value = models.TextField()

    class Meta:
        unique_together = (('user', 'key'),)
        db_table = 'auth_user_data'


class DataContextManager(models.Manager):
    def get_queryset(self):
        # Filter by thread local data context
        from keops.modules.base.middleware import get_data_context
        return super(DataContextManager, self).get_queryset().filter(company_id=get_data_context())


class CompanyModel(models.Model):
    company = models.ForeignKey(Company, visible=False)

    objects = DataContextManager()

    class Meta:
        abstract = True
