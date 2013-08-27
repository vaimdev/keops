
import datetime
from datetime import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from keops.db import models

# User follow object
class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False, related_name='+')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    join_date = models.DateTimeField(_('date/time'), auto_now_add=True, null=False)

    class Meta:
        db_table = 'comment_follow'

# User content comment
class CommentContent(models.Model):
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
        db_table = 'comment_content'

# User comment message
class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False)
    send_date = models.DateTimeField(_('date/time send'), default=datetime.datetime.now())
    message = models.TextField(_('comment'))
    read_date = models.DateTimeField(_('date/time read'))
    starred = models.BooleanField(_('starred'))
    job = models.BooleanField(_('job'))

    class Meta:
        db_table = 'comment_message'
