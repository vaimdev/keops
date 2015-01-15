
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from keops.db import models
from .module import *

class View(ModuleElement):
    FORMATS = (
        ('django', 'Django template'),
        ('mako', 'Mako template'),
        ('html', 'HTML'),
        ('xml', 'XML'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
    )
    TYPE = (
        ('class', 'Class Based View'),
        ('view', 'Custom View'),
        ('tree', 'Tree'),
        ('form', 'Form'),
        ('search', 'Search'),
        ('graph', 'Graph'),
        ('calendar', 'Calendar'),
        ('diagram', 'Diagram'),
        ('gantt', 'Gantt'),
        ('kanban', 'Kanban'),
    )
    name = models.CharField(_('name'), max_length=128, null=False, unique=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    sequence = models.SmallIntegerField(_('sequence'), default=32)
    description = models.CharField(_('description'), max_length=256)
    view_format = models.CharField(_('format'), max_length=16, choices=FORMATS, default='django')
    view_type = models.CharField(_('type'), max_length=16, null=False, default='tree')
    definition = models.TextField(_('definition'))
    ancestor = models.ForeignKey('self', verbose_name=_('ancestor view'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('view')
        verbose_name_plural = _('views')

class CustomView(models.Model):
    view = models.ForeignKey(View, verbose_name=_('view'), null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False, on_delete=models.CASCADE)
    definition = models.TextField(_('definition'))

class Report(ModuleElement):
    name = models.CharField(_('name'), max_length=256, null=False, unique=True)
    description = models.CharField(_('description'), max_length=256)
    definition = models.TextField(_('definition'))

    class Meta:
        verbose_name = _('report')

    class Extra:
        default_fields = ('name', 'description')
        field_groups = {
            'list_fields': ('name', 'description')
        }
