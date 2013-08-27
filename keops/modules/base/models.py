
import json
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from keops.db import models

from .auth import *

#class Config(models.Model):
#    log_actions = models.BooleanField(_('log actions'), help_text=_('Log all user actions'))
#    log_changes = models.BooleanField(_('log changes'), _('Log all user changes'))
    
#    class Meta:
#        verbose_name = _('config')

class ElementManager(models.Manager):
    def get_by_natural_key(self, id):
        """Filter id on ModelData table, and get the related content object."""
        return ModelData.objects.get(name=id).content_object
    
    def filter_by_user(self, user, **kwargs):
        return self.filter(**kwargs).filter(Q(groups__id__in=user.groups.all().values('id')) | Q(users=user))

class Element(models.Model):
    users = models.ManyToManyField('base.User', verbose_name=_('users'))
    groups = models.ManyToManyField('auth.Group', verbose_name=_('groups'))
    
    objects = ElementManager()
    
class Module(Element):
    app_label = models.CharField(_('application label'), max_length=64, unique=True)
    name = models.CharField(_('name'), max_length=128, null=False, unique=True)
    description = models.CharField(_('description'), max_length=256)
    author = models.CharField(_('author'), max_length=64)
    license_type = models.CharField(_('license'), max_length=64, help_text='Commercial, BSD, MIT, LGPL, GPL...')
    version = models.CharField(max_length=32, verbose_name=_('version'))
    db_version = models.IntegerField(_('DB version'), help_text=_('Database version'), null=True)
    last_update = models.IntegerField(_('last update'))
    icon = models.CharField(_('icon'), max_length=256)
    details = models.TextField(_('details'))
    dependencies = models.TextField(_('dependencies'))
    tooltip = models.CharField(_('tooltip'), max_length=64)
    visible = models.BooleanField(_('visible'), default=True)

    class Meta:
        verbose_name = _('module')
        
    def __str__(self):
        return '%s (%s)' % (self.app_label, self.name)
        
class ModuleElement(Element):
    module = models.ForeignKey(Module, verbose_name=_('module'))
    
    class Meta:
        db_table = 'base_module_element'
        
class BaseModelManager(ElementManager):
    def get_by_natural_key(self, app_label, model):
        return BaseModel.objects.get(content_type=ContentType.objects.get_by_natural_key(app_label, model))
    
class BaseModel(ModuleElement):
    content_type = models.OneToOneField(ContentType)
    ancestor = models.ForeignKey('self', verbose_name=_('base model'))
    #name = models.CharField(max_length=64, verbose_name=_('Class Name'), null=False, unique=True)
    #db_table = models.CharField(max_length=64, verbose_name=_('Table Name'), null=False, db_index=True)
    description = models.CharField(_('description'), max_length=128)
    is_abstract = models.BooleanField(_('is abstract'), default=False)
    
    objects = BaseModelManager()

    class Meta:
        db_table = 'base_model'
        verbose_name = _('model')
        
    def __str__(self):
        return '%s.%s' % (self.content_type.app_label, self.content_type.model)
        
class Config(models.Model):
    update_URL = models.CharField(max_length=64, verbose_name=_('update URL'))
    support_URL = models.CharField(max_length=64, verbose_name=_('support URL'))

class Field(Element):
    model = models.ForeignKey(BaseModel, verbose_name=_('model'), null=False)
    name = models.CharField(max_length=64, null=False, unique=True, verbose_name=_('name'))
    description = models.CharField(_('description'), max_length=64)
    help_text = models.CharField(_('help text'), max_length=128)

    class Meta:
        db_table = 'base_field'
        verbose_name = _('field')
        verbose_name_plural = _('fields')

class View(ModuleElement):
    FORMATS = (
        ('django', 'Django template'),
        ('mako', 'Mako template'),
        ('jinja', 'Jinja template'),
        ('xml', 'XML'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
    )
    name = models.CharField(_('name'), max_length=128, null=False, unique=True)
    description = models.CharField(_('description'), max_length=256)
    format = models.CharField(_('format'), max_length=16, choices=FORMATS, default='django')
    model = models.ForeignKey(BaseModel, verbose_name=_('model'))
    definition = models.TextField(_('definition'))

    class Meta:
        verbose_name = _('view')
        verbose_name_plural = _('views')

class Report(ModuleElement):
    name = models.CharField(_('name'), max_length=256, null=False, unique=True)
    description = models.CharField(_('description'), max_length=256)
    
    class Meta:
        verbose_name = _('report')

class Action(ModuleElement):
    action_types = {}
    name = models.CharField(_('name'), max_length=128, null=False, unique=True)
    short_description = models.CharField(_('short description'), max_length=32)
    description = models.CharField(max_length=256, verbose_name=_('description'))
    action_type = models.CharField(_('type'), max_length=32, null=False)
    context = models.TextField(_('context'))

    class Meta:
        verbose_name = _('actions')
        
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
    
    class Meta:
        db_table = 'base_view_action'
        verbose_name = _('view action')
        verbose_name_plural = _('view actions')
        
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
    model = models.ForeignKey(BaseModel, verbose_name=_('model'))
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
        
    def execute(self, request, *args, **kwargs):
        from .views import actions
        return actions.response_form(request, self)

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

class ModelData(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    can_change = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'base_model_data'

class Attachment(models.Model):
    name = models.CharField(max_length=128, null=False, verbose_name=_('name'))
    description = models.TextField(_('description'))
    type = models.CharField(_('type'), max_length=16, choices=(('url', 'URL'), ('file', _('File'))))
    body = models.BinaryField(_('body'))
    url = models.URLField('URL')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        db_table = 'base_attachment'
        verbose_name = _('attachment')
        verbose_name = _('attachments')
        
class Default(models.Model):
    model = models.ForeignKey(BaseModel, verbose_name=_('model'), on_delete='CASCADE')
    field = models.CharField(_('field'), max_length=64)
    value = models.TextField(_('value'))
    user = models.ForeignKey('base.User', verbose_name=_('user'), help_text=_('leave blank for all users'))
    
    class Meta:
        db_table = 'base_default'
        verbose_name = _('default field value')
        verbose_name_plural = _('default fields values')

class Attribute(models.Model):
    ATT_TYPE =(
        ('text', _('Text')),
        ('date', _('Date')),
        ('time', _('Time')),
        ('datetime', _('Date/Time')),
        ('money', _('Money')),
        ('integer', _('Integer')),
        ('float', _('Float')),
        ('textarea', _('Text Area')),
        ('choice', _('Choice')),
        ('multiplechoice', _('Multiple Choices')),
        ('foreignkey', _('Foreign Key')),
        ('logical', _('Logical')),
        ('image', _('Image')),
        ('file', _('File')),
    )
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(_('attribute name'), max_length=64)
    type = models.CharField(_('attribute type'), max_length=16, choices=ATT_TYPE)
    widget_attrs = models.TextField(_('widget attributes'))
    default_value = models.TextField(_('default value'), help_text=_('Default attribute value'))
    trigger = models.TextField(_('attribute trigger'), help_text=_('Trigger attribute code'))
    
    class Meta:
        db_table = 'base_attribute'

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute)
    object_id = models.PositiveIntegerField()
    text_value = models.CharField(max_length=1024)
    texta_value = models.TextField()
    logical_value = models.BooleanField()
    #file_value = models.FileField()
    fk_value = models.PositiveIntegerField()
    int_value = models.IntegerField()
    decimal_value = models.MoneyField()
    date_value = models.DateTimeField()
    
    class Meta:
        db_table = 'base_attribute_value'

class ContentAuthor(models.Model):
    """User/author content object log."""
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), null=False)
    object_id = models.PositiveIntegerField(_('object id'), null=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('created by'), null=False, related_name='+')
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'), null=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('modified by'), related_name='+')
    modified_on = models.DateTimeField(auto_now=True, verbose_name=_('modified on'))

    class Meta:
        db_table = 'base_content_author'

class UserLog(models.Model):
    """User log record."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=False, related_name='+')
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), null=False)
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    operation = models.CharField(max_length=64, null=False) # insert, update, delete, print...
    description = models.TextField()
    log_time = models.DateTimeField(_('date/time'), null=False, auto_now_add=True)

    class Meta:
        db_table = 'base_user_log'
