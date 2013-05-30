
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from keops.modules.base import models as base

class FormAction(base.Action):
    VIEW_TYPE = (
        ('form', 'Form'),
        ('list', 'List'),
        ('chart', 'Chart'),
        ('calendar', 'Calendar'),
        ('kanban', 'Kanban'),
    )
    form = models.ForeignKey(base.View, verbose_name=_('form'))
    model = models.ForeignKey(base.BaseModel, verbose_name=_('model'))
    target = models.CharField(_('target'), max_length=32)
    view_type = models.CharField(_('initial view'), max_length=16, choices=VIEW_TYPE, default='form')
    view_modes = models.CharField(_('view modes'), max_length=64)
    
    def get_action_type(self):
        return 'form'

    class Meta:
        db_table = 'base_form_action'
        verbose_name = _('form action')
        verbose_name_plural = _('form actions')
        
    def execute(self, request, *args, **kwargs):
        from .views import forms
        return forms.response_action(request, self)

class ReportAction(base.Action):
    report = models.ForeignKey(base.Report, verbose_name=_('report'))

    class Meta:
        db_table = 'base_report_action'
        verbose_name = _('report action')
        verbose_name_plural = _('report actions')

    def get_action_type(self):
        return 'report'
    
    def execute(self, request, *args, **kwargs):
        pass
        
class Menu(base.Menu):
    class Meta:
        db_table = 'base_menu'
        proxy = True

    ## Auto create report action for target menu item
    def get_report(self):
        if self.action and self.action.action_type == 'show report':
            return ReportAction.objects.get(pk=self.action.pk).report
    def set_report(self, report):
        if isinstance(report, str):
            try:
                rep = Report.objects.get(name=report)
            except:
                rep = Report.objects.create(name=report)
            report = rep
        action = ReportAction.objects.create(name='%s "%s"' % (_('ShowReport'), report.name), report=report)
        self.action = action
        self.image = '/static/orun-erp/icons/page.png'
    report = property(get_report, set_report)

# Register form action types
base.Action.action_types['form'] = FormAction
base.Action.action_types['report'] = ReportAction
