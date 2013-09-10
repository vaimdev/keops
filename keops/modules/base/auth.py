
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth
from django.contrib.auth.models import Group
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
        db_table = 'base_user_content'

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
        db_table = 'base_user_log'

