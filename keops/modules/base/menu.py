
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from .module import *
from .action import *

class MenuManager(ElementManager):
    def add_menu(self, path, action, icon=None):
        menu = self.model()
        menu.full_name = path
        menu.action = action
        menu.image = icon
        menu.save()

class Menu(ModuleElement):
    name = models.CharField(_('name'), max_length=128, null=False, db_index=True)
    parent = models.ForeignKey('self', verbose_name=_('parent'))
    action = models.ForeignKey(Action, verbose_name=_('action'))
    image = models.CharField(_('image'), max_length=256, help_text=_('menu image file path'))
    sequence = models.PositiveIntegerField(_('sequence'), help_text=_('menu item sequence'), default=0, db_index=True)

    objects = MenuManager()

    class Meta:
        db_table = 'base_menu'
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')
        ordering = ['sequence', 'id']

    def __str__(self):
        return self.get_full_name()

    @property
    def is_leaf(self):
        return self.__class__.objects.filter(parent_id=self.pk).count() == 0

    def get_full_name(self):
        parents = []
        parent = self
        while parent:
            parents.insert(0, parent.name)
            parent = parent.parent
        return '/'.join(parents)
    def set_full_name(self, path):
        cls = self.__class__
        menu = None
        parents = path.split('/')
        self.name = parents[-1]
        for item in parents[:-1]:
            parent = menu
            try:
                menu = cls.objects.get(parent_id=menu, name=item)
            except:
                menu = None
            if not menu:
                menu = cls.objects.create(name=item.replace('\\', '/'), parent=parent, module_id=self.module_id)
        self.parent = menu
    full_name = property(get_full_name, set_full_name)

    ## Auto create model form action for target menu item
    def get_model(self):
        if self.action and self.action.action_type == 'form':
            return FormAction.objects.get(pk=self.action.pk).model
    def set_model(self, model):
        from keops.modules.base.models import BaseModel
        if isinstance(model, str):
            model = model.split('.')
            model = BaseModel.objects.get(content_type__app_label=model[0], content_type__model=model[1])
        action = FormAction.objects.create(name='%s "%s.%s"' % (('showmodel',) + model.content_type.natural_key()), model=model)
        self.action = action
        self.image = '/static/keops/icons/page.png'
    model = property(get_model, set_model)

    ## Auto create form action for target menu item
    def get_form(self):
        if self.action and self.action.action_type == 'form':
            return FormAction.objects.get(pk=self.action.pk).view
    def set_form(self, form):
        if isinstance(form, str):
            form = View.objects.get(name=form)
        action = FormAction.objects.create(name='%s "%s"' % ('showform', form.name), view=form)
        self.action = action
        self.image = '/static/keops/icons/page.png'
    form = property(get_form, set_form)

    ## Auto create report action for target menu item
    def get_report(self):
        if self.action and self.action.action_type == 'report':
            return ReportAction.objects.get(pk=self.action.pk).report
    def set_report(self, report):
        if isinstance(report, str):
            try:
                rep = Report.objects.get(name=report)
            except:
                rep = Report.objects.create(name=report)
            report = rep
        action = ReportAction.objects.create(name='%s "%s"' % ('showreport', report.name), report=report)
        self.action = action
        self.image = '/static/keops/icons/page.png'
    report = property(get_report, set_report)

