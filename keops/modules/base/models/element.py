from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from keops.db import models


class ModelData(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    can_change = models.BooleanField(default=True)

    class Meta:
        db_table = 'base_model_data'


class ElementManager(models.Manager):
    def get_by_natural_key(self, id):
        """
        Filter id on ModelData table, and get the related content object.
        """
        return ModelData.objects.using(self.db).get(name=id).content_object

    def filter_by_user(self, user, **kwargs):
        return self.filter(**kwargs).filter(Q(groups__id__in=user.groups.all().values('id')) | Q(users=user))


class Element(models.Model):
    users = models.ManyToManyField('base.User', verbose_name=_('users'), custom_attrs={'page': _('Permissions')})
    groups = models.ManyToManyField('auth.Group', verbose_name=_('groups'), custom_attrs={'page': _('Permissions')})

    objects = ElementManager()

