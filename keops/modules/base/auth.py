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
from keops.db import models
from .element import ElementManager


Group.add_to_class('module_category', models.ForeignKey('base.modulecategory', verbose_name=_('category')))


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
    is_customer = models.BooleanField(_('is customer'), default=False)
    is_supplier = models.BooleanField(_('is supplier'), default=False)
    is_employee = models.BooleanField(_('is employee'), default=False)
    is_company = models.BooleanField(_('is company'), default=False)
    address = models.CharField(_('address'), max_length=256)
    city = models.CharField(_('city'), max_length=64)
    zip_code = models.CharField(_('zip'), max_length=32)
    country = models.ForeignKey('base.country', verbose_name=_('country'))
    email = models.EmailField('email')
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


class AbstractBaseUser(models.Model):
    password = models.CharField(_('password'), max_length=128)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_active = True

    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def get_username(self):
        "Return the identifying username for this User"
        return getattr(self, self.USERNAME_FIELD)

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = auth.make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return auth.check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = auth.make_password(None)

    def has_usable_password(self):
        return auth.is_password_usable(self.password)

    def get_full_name(self):
        raise NotImplementedError()

    def get_short_name(self):
        raise NotImplementedError()


class PermissionsMixin(models.Model):
    """
    A mixin class that adds the fields and methods necessary to support
    Django's Group and Permission model using the ModelBackend.
    """
    is_superuser = models.BooleanField(_('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))
    groups = models.ManyToManyField(Group, verbose_name=_('groups'),
        blank=True, help_text=_('The groups this user belongs to. A user will '
                                'get all permissions granted to each of '
                                'his/her group.'),
        related_name="user_set", related_query_name="user")
    user_permissions = models.ManyToManyField(auth.Permission,
        verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set", related_query_name="user")

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through his/her
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return auth._user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return auth._user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return auth._user_has_module_perms(self, app_label)


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=30, unique=True, null=False,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_absolute_url(self):
        return "/users/%s/" % auth.urlquote(self.username)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name.split()[0]

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        auth.send_mail(subject, message, from_email, [self.email])


class CompanyManager(ElementManager):
    def get_queryset(self):
        return super(CompanyManager, self).get_queryset().defer('image')  # default defer image


# Company/data context
class Company(Contact):
    """
    Company configuration model.
    """
    parent_company = models.ForeignKey('self')
    currency = models.ForeignKey('base.currency', verbose_name=_('currency'))
    report_style = models.CharField(_('report style'), max_length=64, page=_('Report Configurations'))
    report_header = models.TextField(_('report header'), page=_('Report Configurations'))
    report_footer = models.TextField(_('report footer'), page=_('Report Configurations'))

    objects = CompanyManager()

    class Meta:
        db_table = 'base_company'
        verbose_name = _('company')
        verbose_name_plural = _('companies')

    class Extra:
        display_expression = ('name',)
        field_groups = {
            'list_fields': ('name', 'country', 'website'),
            'search_fields': ('name', 'country', 'website'),
        }


class User(Contact, AbstractUser):
    email_signature = models.TextField(_('e-mail signature'))
    document_signature = models.TextField(_('document signature'))
    company = models.ForeignKey('base.company', verbose_name=_('company'), help_text=_('default user company'), related_name='+')
    companies = models.ManyToManyField('base.company', verbose_name=_('allowed companies'), help_text=_('user allowed companies'))
    status = models.CharField(max_length=16, choices=(('created', _('Created')), ('activated', _('activated'))), visible=False)

    raw_password = property(fset=AbstractUser.set_password)

    REQUIRED_FIELDS = ['email', 'name']

    objects = auth.UserManager()

    class Meta:
        db_table = 'auth_user'

    class Extra:
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
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'), null=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('modified by'), related_name='+')
    modified_on = models.DateTimeField(auto_now=True, verbose_name=_('modified on'))

    class Meta:
        db_table = 'auth_user_content'


# User log definition
ADDITION = 'add'
CHANGE = 'change'
DELETION = 'delete'


class UserLogManager(models.Manager):
    def log_action(self, user_id, content_type_id, object_id, object_repr, action_flag, change_message=''):
        e = self.model(None, None, user_id, content_type_id, smart_text(object_id), object_repr[:200], action_flag, change_message)
        e.save()


class UserLog(models.Model):
    action_time = models.DateTimeField(_('action time'), auto_now=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.TextField(_('object id'), blank=True, null=True, db_index=True)
    object_repr = models.CharField(_('object repr'), max_length=200)
    action_flag = models.CharField(_('action flag'), db_index=True)
    change_message = models.TextField(_('change message'), blank=True)

    objects = UserLogManager()

    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        db_table = 'auth_user_log'
        ordering = ('-action_time',)

    def __repr__(self):
        return smart_text(self.action_time)

    def __str__(self):
        if self.action_flag == ADDITION:
            return ugettext('Added "%(object)s".') % {'object': self.object_repr}
        elif self.action_flag == CHANGE:
            return ugettext('Changed "%(object)s" - %(changes)s') % {
                'object': self.object_repr,
                'changes': self.change_message,
            }
        elif self.action_flag == DELETION:
            return ugettext('Deleted "%(object)s."') % {'object': self.object_repr}

        return ugettext('LogEntry Object')

    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION

    def get_edited_object(self):
        "Returns the edited object represented by this log entry"
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def get_admin_url(self):
        """
        Returns the admin URL to edit the object represented by this log entry.
        This is relative to the Django admin index page.
        """
        # TODO
        return None


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


def user_logged_in(sender, request, user, *args, **kwargs):
    # Load basic user information
    # Select default user company
    request.session['company'] = user.company

django.contrib.auth.user_logged_in.connect(user_logged_in)
