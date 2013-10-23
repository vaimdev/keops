from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth
from django.contrib.auth.models import Group
import django.contrib.auth.signals
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from keops.db import models

class User(auth.AbstractUser):
    email_signature = models.TextField(_('e-mail signature'))
    document_signature = models.TextField(_('document signature'))

    raw_password = property(fset=auth.AbstractUser.set_password)

    REQUIRED_FIELDS = ['email', 'first_name']
    
    class Meta:
        db_table = 'auth_user'

    class Extra:
        field_groups = {
            'list_fields': ('username', 'email', 'first_name', 'last_name'),
            'search_fields': ('username', 'email', 'first_name', 'last_name'),
        }

    def get_user_data(self, key, default=None):
        data = UserData.objects.using(self._state.db).filter(user=self, key=key)
        if data:
            return data[0]
        else:
            return default

    def set_user_data(self, key, value):
        data = UserData.objects.using(self._state.db).filter(user=self, key=key)
        if data:
            data = data[0]
        else:
            data = UserData(key=key)
        data.value = value
        data.save(db=db)

    def __str__(self):
        return self.username + (self.first_name and (' (' + self.first_name + (self.last_name and (' ' + self.last_name) or '') + ')') or '')

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

class UserLog(models.Model):
    """
    User log record.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False, related_name='+')
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), null=False, related_name='+')
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    operation = models.CharField(max_length=64, null=False) # create, read, update, delete, print...
    description = models.TextField()
    log_time = models.DateTimeField(_('date/time'), null=False, auto_now_add=True)

    class Meta:
        db_table = 'auth_log'

class UserData(models.Model):
    user = models.ForeignKey(User, null=False)
    key = models.CharField(max_length=64, db_index=True)
    value = models.TextField()

    class Meta:
        unique_together = (('user', 'key'),)
        db_table = 'auth_user_data'

def user_logged_in(sender, request, user, *args, **kwargs):
    # Load basic user information
    # Select last login user company
    db = user._state.db
    company = UserData.objects.using(db).filter(user=user, key='auth.profile.last_company')
    from .models import Company
    if company:
        company = Company.objects.using(db).get(pk=company[0].value)
    else:
        # TODO check permission
        company = Company.objects.using(db).all()[0]
        UserData.objects.create(user=user, key='auth.profile.last_company', value=company.pk)
    request.session['company'] = company

django.contrib.auth.user_logged_in.connect(user_logged_in)
