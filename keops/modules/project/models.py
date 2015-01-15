from django.utils.translation import ugettext_lazy as _
from keops.db import models

STATUS = (
    ('draft', _('Draft')),
    ('open', _('In Progress')),
    ('pending', _('Pending')),
    ('done', _('Done')),
    ('cancelled', _('Cancelled'))
)


class Category(models.Model):
    name = models.CharField(null=False, unique=True)


class TaskType(models.Model):
    name = models.CharField(unique=True, null=False)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS)

    class Meta:
        db_table = 'project_task_type'


class Project(models.Model):
    manager = models.ForeignKey('base.User')


class Task(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS)
