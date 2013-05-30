
import datetime
from datetime import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from keops.db import models

class Contact(models.Model):
    name = models.CharField(_('name'), max_length=100, null=False)
    email = models.EmailField('e-mail')
    
    class Meta:
        abstract = True
        verbose_name = _('contact')

# User follow record
class UserContent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    join_date = models.DateTimeField(_('date/time'), default=datetime.datetime.now())

    class Meta:
        db_table = 'communication_user_content'

class UserContentComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    comment = models.TextField(_('comment'))
    submit_date = models.DateTimeField(_('date/time submitted'), default=datetime.datetime.now())
    ip_address = models.GenericIPAddressField(_('IP address'), unpack_ipv4=True)
    is_public = models.BooleanField(_('is public'), default=True,
                    help_text=_('Uncheck this box to make the comment effectively ' \
                                'disappear from the site.'))
    is_removed = models.BooleanField(_('is removed'), default=False,
                    help_text=_('Check this box if the comment is inappropriate. ' \
                                'A "This comment has been removed" message will ' \
                                'be displayed instead.'))

    class Meta:
        db_table = 'communication_user_content_comment'

class UserMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False)
    send_date = models.DateTimeField(_('date/time send'), default=datetime.datetime.now())
    message = models.TextField(_('comment'))
    read_date = models.DateTimeField(_('date/time read'))
    starred = models.BooleanField(_('starred'))
    todo = models.BooleanField(_('to do'))

    class Meta:
        db_table = 'communication_user_message'
