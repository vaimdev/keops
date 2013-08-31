
import datetime
from datetime import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from keops.db import models

# TODO: Implement full enterprise social network here

# Comment enterprise social network group
class Group(models.Model):
    PRIVACY = (
        ('public', _('Public')),
        ('private', _('Private')),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    name = models.CharField(_('name'), max_length=100, null=False, unique=True, help_text=_('Group name'))
    description = models.TextField(_('description'))
    email = models.EmailField()
    privacy = models.CharField(max_length=16, choices=PRIVACY, default='public', null=False)
    # TODO: add image field here

    class Meta:
        db_table = 'comment_group'

# User follow object
class Follow(models.Model):
    """
    Used to user follow any allowed content object.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='+')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    join_date = models.DateTimeField(_('date/time'), auto_now_add=True, null=False)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment_follow'

# User content comment
class Comment(models.Model):
    """
    Provides user comment to any allowed content object.
    """
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
    """
    User message box.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False)
    send_date = models.DateTimeField(_('date/time send'), default=datetime.datetime.now())
    message = models.TextField(_('comment'))
    read_date = models.DateTimeField(_('date/time read'))
    starred = models.BooleanField(_('starred'))
    job = models.BooleanField(_('job'))

    class Meta:
        db_table = 'comment_message'
