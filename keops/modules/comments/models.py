# Implement enterprise social network
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
        ('groups', _('Selected groups')),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    name = models.CharField(_('name'), max_length=100, null=False, unique=True, help_text=_('Group name'))
    description = models.TextField(_('description'))
    email = models.EmailField()
    privacy = models.CharField(max_length=16, choices=PRIVACY, default='public', null=False)
    groups = models.ManyToManyField('self')
    # TODO: add image field here

    class Meta:
        db_table = 'comments_group'

# Object followers
class Follower(models.Model):
    """
    Used to user follow any allowed content object.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='+')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    join_date = models.DateTimeField(_('date/time'), auto_now_add=True, null=False)
    active = models.BooleanField(default=True)
    subtypes = models.ManyToManyField('comments.Subtype')

    class Meta:
        db_table = 'comments_follower'

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
        db_table = 'comments_content'

class Subtype(models.Model):
    name = models.CharField(_('name'), max_length=32, null=False)
    description = models.CharField(_('description'), max_length=128)
    parent = models.ForeignKey('self')
    content_type = models.ForeignKey(ContentType)
    relation_field = models.CharField(_('relation field'))
    default = models.BooleanField(_('default'), default=True)

class Message(models.Model):
    """
    Message model for system notification.
    """
    TYPE = (
        ('email', 'E-mail'),
        ('comment', _('Comment')),
        ('notification', _('Notification')),
    )
    message_type = models.CharField(_('type'), choices=TYPE)
    #message_from =
    parent = models.ForeignKey('self', related_name='+')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    subject = models.CharField(_('subject'), max_length=128)
    date = models.DateField(_('date'))
    body = models.TextField(_('body'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False)
    send_date = models.DateTimeField(_('date/time send'), default=datetime.datetime.now())
    message = models.TextField(_('comment'))
    read_date = models.DateTimeField(_('date/time read'))
    starred = models.BooleanField(_('starred'))
    job = models.BooleanField(_('job'))

    class Meta:
        db_table = 'comments_message'

class Mail(models.Model):
    STATUS = (
        ('outgoing', _('Outgoing')),
        ('sent', _('Sent')),
        ('received', _('Received')),
        ('failed', _('Delivery failed')),
        ('cancelled', _('Cancelled')),
    )
    message = models.ForeignKey(Message, verbose_name=_('message'), null=False, on_delete=models.CASCADE)
    status = models.CharField(_('status'), choices=STATUS, readonly=True)
    auto_delete = models.BooleanField(_('auto delete'))
    references = models.TextField(_('references'))
    email_from = models.EmailField()
    email_to = models.TextField()
    email_cc = models.TextField()
    reply_to = models.EmailField()
    body = models.TextField(_('body'))
    is_notification = models.BooleanField(_('is notification'))

class Notification(models.Model):
    partner = models.ForeignKey('contacts.Contact', null=False)
    message = models.ForeignKey(Message, null=False)
    read = models.BooleanField(_('read'), default=False)
    starred = models.BooleanField(_('starred'), default=False)

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, verbose_name=_('message'), null=False, on_delete=models.CASCADE)
