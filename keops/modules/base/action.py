import json
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from .module import *
from .ui import *

class ActionManager(ElementManager):
    def get_by_model_name(self, model):
        model = model.split('.')
        ct = ContentType.objects.get(app_label=model[0], model=model[1])
        from .models import BaseModel
        model = BaseModel.objects.get(content_type=ct)
        try:
            return FormAction.objects.get(model=model)
        except:
            return

class Action(ModuleElement):
    action_types = {}
    name = models.CharField(_('name'), max_length=128, null=False, unique=True)
    short_description = models.CharField(_('short description'), max_length=32)
    description = models.CharField(max_length=256, verbose_name=_('description'))
    action_type = models.CharField(_('type'), max_length=32, null=False)
    context = models.TextField(_('context'))

    objects = ActionManager()

    class Meta:
        verbose_name = _('action')
        verbose_name_plural = _('actions')

    class Extra:
        field_groups = {
            'list_fields': ('name', 'short_description', 'description', 'action_type')
        }

    def get_absolute_url(self):
        return 'action/%i/' % self.pk

    def get_action_type(self):
        return None

    def get_context(self):
        if self.context:
            return json.dumps(self.context)
        else:
            return {}

    def save(self, *args, **kwargs):
        self.action_type = self.get_action_type()
        super(Action, self).save(*args, **kwargs)

    def execute(self, request, *args, **kwargs):
        return self.action_types[self.action_type].objects.get(pk=self.pk).execute(request, *args, **kwargs)

class ViewAction(Action):
    view = models.ForeignKey(View, verbose_name=_('view'))
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))

    class Meta:
        db_table = 'base_view_action'
        verbose_name = _('view action')
        verbose_name_plural = _('view actions')

    class Extra:
        field_groups = {
            'list_fields': ('name', 'short_description', 'description', 'content_type')
        }

    def get_action_type(self):
        return 'view'

class URLAction(Action):
    url = models.URLField('URL', help_text=_('target URL'))
    target = models.CharField(_('target'), max_length=32)

    class Meta:
        db_table = 'base_url_action'
        verbose_name = _('URL action')
        verbose_name_plural = _('URL actions')

    def get_action_type(self):
        return 'url'

class FormAction(Action):
    VIEW_TYPE = (
        ('form', 'Form'),
        ('list', 'List'),
        ('chart', 'Chart'),
        ('calendar', 'Calendar'),
        ('kanban', 'Kanban'),
    )
    VIEW_STATE = (
        ('read', _('Read')),
        ('write', _('Write')),
        ('create', _('Create')),
        ('delete', _('Delete')),
    )
    view = models.ForeignKey(View, verbose_name=_('view'))
    model = models.ForeignKey('base.BaseModel', verbose_name=_('model'))
    target = models.CharField(_('target'), max_length=32)
    view_type = models.CharField(_('initial view'), max_length=16, choices=VIEW_TYPE, default='list')
    view_types = models.CharField(_('view types'), max_length=64)
    state = models.CharField(_('state'), max_length=16)

    def get_action_type(self):
        return 'form'

    class Meta:
        db_table = 'base_form_action'
        verbose_name = _('form action')
        verbose_name_plural = _('form actions')

    class Extra:
        field_groups = {
            'list_fields': ('name', 'short_description', 'description', 'view', 'model')
        }

    def execute(self, request, *args, **kwargs):
        from .views import actions
        return actions.response_form(request, self, *args, **kwargs)

class ReportAction(Action):
    report = models.ForeignKey(Report, verbose_name=_('report'))

    class Meta:
        db_table = 'base_report_action'
        verbose_name = _('report action')
        verbose_name_plural = _('report actions')

    def get_action_type(self):
        return 'report'

    def execute(self, request, *args, **kwargs):
        pass

# Register form action types
Action.action_types['view'] = ViewAction
Action.action_types['url'] = URLAction
Action.action_types['form'] = FormAction
Action.action_types['report'] = ReportAction
