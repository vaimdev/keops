import datetime
from collections import OrderedDict
from importlib import import_module
import copy
import json
from django.utils import six
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils.text import capfirst
from keops.contrib.reports import Reports, ReportLink
from keops.http import HttpJsonResponse
from keops.utils import field_text
from .forms import View

views = import_module(settings.FORM_RENDER_MODULE)

class FieldLine(object):
    def __init__(self, form, fields):
        self.form = form
        self.fields = fields
    
    def __iter__(self):
        for field in self.fields:
            yield self.form.get_formfield(field)

class Fieldset(object):
    def __init__(self, name, form, fieldset):
        self.name = name
        self.form = form
        self.fieldset = fieldset
        lines = fieldset['fields']
        self.lines = []
        for line in lines:
            if not isinstance(line, (tuple, list)):
                line = (line,)
            self.lines.append(line)
    
    def __iter__(self):
        for line in self.lines:
            yield FieldLine(self.form, line)
            
class TabPage(object):
    def __init__(self, name, form, fieldsets):
        self.form = form
        self.name = name
        self.fieldsets = fieldsets

    def __iter__(self):
        for name, fieldset in self.fieldsets:
            yield Fieldset(name, self.form, fieldset)

class ModelAdminBase(type):
    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)
        if attrs.get('default_admin', None):
            new_class()
        return new_class

def admin_formfield_callback(self, field, **kwargs):
    from keops.db import models
    f = field.formfield(**kwargs)
    if f:
        if f and f.help_text:
            f.widget.attrs.setdefault('tooltip', f.help_text)
        if isinstance(f, forms.ModelChoiceField):
            f.widget.attrs.setdefault('class', 'form-long-field')
        elif isinstance(field, models.TextField):
            f.widget.attrs.setdefault('class', 'form-long-field')
        elif isinstance(f, (forms.DateField, forms.DateTimeField)):
            f.widget.attrs.setdefault('class', 'form-date-field')
        elif isinstance(f, forms.IntegerField):
            f.widget.attrs.setdefault('class', 'form-int-field')
        elif isinstance(f, forms.DecimalField):
            f.widget.attrs.setdefault('class', 'form-decimal-field')
        elif isinstance(f, forms.CharField) and f.max_length and f.max_length <= 15:
            f.widget.attrs.setdefault('class', 'form-small-field')
        elif isinstance(f, forms.CharField) and f.max_length and f.max_length <= 20:
            f.widget.attrs.setdefault('class', 'form-20c-field')
        else:
            f.widget.attrs.setdefault('class', 'form-long-field')
        return f

class ModelAdmin(six.with_metaclass(ModelAdminBase, View)):
    formfield_callback = admin_formfield_callback
    default_admin = False
    template_name = 'keops/forms/model_form.html'
    list_template = 'keops/forms/list_form.html'
    fields = ()
    exclude = ()
    readonly_fields = ()
    list_display = ()
    pages = ()
    search_fields = ()
    columns = 2
    printable_fields = ()
    reports = ()
    formfield_overrides = None

    toolbar_actions = ['create', 'read', 'update', 'delete', 'print', 'delete', 'search']

    actions = []
    model = None
    title = None
    label = None
    help_text = ''

    model_form = None

    def __init__(self, admin=None):
        self.bound_fields = {}
        self.admin = admin
        self.model_fields = []
        self._prepared = False
        self._form = None
        self._model_form = None
        if self.model:
            if self.default_admin:
                self.contribute_to_class(self.model, '_admin')

    def contribute_to_class(self, cls, name):
        cls._admin = self
        self.model = cls
        if self.admin:
            dsgn_attrs = dict(self.admin.__dict__.copy())
            # ignore private/internal items
            attrs = [k for k in dsgn_attrs if not k.startswith('_')]
            for attr in attrs:
                setattr(self, attr, dsgn_attrs[attr])
            del self.admin

    def _prepare(self):
        if self._prepared:
            return
        from django.contrib.contenttypes import generic
        extra = getattr(self.model, 'Extra', None)
        if extra:
            if not self.fields and extra.field_groups and extra.field_groups.get('display_fields', None):
                self.fields = extra.field_groups['display_fields']
            if not self.list_display and extra.field_groups and extra.field_groups.get('list_fields', None):
                self.list_display = extra.field_groups['list_fields']
            if not self.printable_fields and extra.field_groups and extra.field_groups.get('printable_fields', None):
                self.printable_fields = extra.field_groups['printable_fields']
            if not self.reports and getattr(extra, 'reports', None):
                self.reports = Reports([ReportLink(report, import_module(self.model.__module__)) for report in extra.reports])
        if self.model._meta.abstract:
            return
        from django.db import models
        model_fields = self.model._meta.all_fields + self.model._meta.many_to_many
        self.model_fields = model_fields
        if not self.fields:
            self.fields = [f.name for f in model_fields if not f.name in self.exclude and not isinstance(f, (
                models.AutoField, generic.GenericForeignKey)) and\
                f.custom_attrs.get('visible', not f.primary_key)]
        if not self.list_display:
            self.list_display = [f.name for f in self.model._meta.all_fields if not f.name in self.exclude and not\
                isinstance(f, (models.AutoField, models.ManyToManyField)) and\
                f.custom_attrs.get('visible', not f.primary_key)]
        if not self.printable_fields:
            self.printable_fields = self.list_display

        if not self.pages:
            pages = OrderedDict()

        if not self.readonly_fields:
            readonly_fields = []

        for field in model_fields:
            if not field.name in self.fields:
                continue
            if not self.pages:
                attrs = field.custom_attrs
                page = pages.setdefault(str(attrs.page or ''), OrderedDict())
                fieldset = page.setdefault(str(attrs.fieldset or ''), {'fields': []})
                fieldset['fields'].append(field.name)
            if not self.readonly_fields and field.readonly:
                readonly_fields.append(field.name)

        if not self.pages and pages:
            for page, fieldsets in pages.items():
                pages[page] = tuple(fieldsets.items())
            self.pages = tuple(pages.items())

        if not self.readonly_fields and readonly_fields:
            self.readonly_fields = readonly_fields

        if self.search_fields:
            # set search field to __icontains
            for i, f in enumerate(self.search_fields):
                if not '__' in f:
                    self.search_fields[i] = '%s__icontains' % f
        elif not self.search_fields or not self.display_expression:
            search_fields = ''
            for f in self.model_fields:
                try:
                    field = self.model._meta.get_field(f.name)
                    if isinstance(field, models.CharField):
                        search_fields = ['%s__icontains']
                        break
                except:
                    pass
            self.search_fields = self.search_fields or search_fields or (self.fields and [self.fields[0]]) or ()
            
        self.title = self.title or self.model._meta.verbose_name_plural
        self.label = self.label or self.model._meta.verbose_name
        self.help_text = self.help_text or getattr(self.model.Extra, 'help_text', '')

    def _prepare_form(self):
        self._prepare()
        for name in self.fields:
            field = None
            for f in self.model_fields:
                if f.name == name:
                    field = f
                    break

            if field and not name in self.bound_fields:
                if name in self.form.fields:
                    f = self.form.fields[name]
                else:
                    f = field.formfield()
                    self.form.fields[name] = f
                self.bound_fields[name] = self.form[name]
                f.target_attr = field
        self._prepared = True

    def __iter__(self):
        for page, fieldsets in self.pages:
            yield TabPage(page, self, fieldsets)

    def render_form(self, cols=None, exclude=[], state=None):
        self._prepare_form()
        return views.render_form(self, cols=cols, exclude=exclude, state=state)

    @property
    def form(self):
        """
        Return default form instance.
        """
        if not self._form:
            self._form = self.model_form()
        return self._form

    @property
    def model_form(self):
        if not self._model_form:
            self._model_form = forms.models.modelform_factory(self.model, formfield_callback=self.formfield_callback)
        return self._model_form

    def get_printable_fields(self):
        self._prepare()
        return self.printable_fields

    def _prepare_context(self, request, context):
        context.update({
            'model': self.model,
            'model_name': '%s' % str(self.model._meta),
        })
        
    def view(self, request, view_type, **kwargs):
        self._prepare_form()
        if view_type == 'list':
            v = self.list_view
        else:
            self._prepare_change_view(request, kwargs)
            v = super(ModelAdmin, self).view
        return v(request, **kwargs)
    
    def _prepare_change_view(self, request, context):
        context['form_view'] = self.render_form()
        pk = request.GET.get('pk')
        if pk:
            context['pk'] = pk
        self._prepare_context(request, context)

    def list_view(self, request, **kwargs):
        from django.db import models
        kwargs['query'] = request.GET.get('query', '')
        kwargs['fields'] = [ (views.get_filter(f, self.model)[0], self.get_formfield(f).label) for f in self.list_display ]
        kwargs['list_display'] = [ '<td%s>{{item.%s}}</td>' % views.get_filter(f, self.model) for f in self.list_display ]
        self._prepare_context(request, kwargs)
        kwargs.setdefault('pagesize', 50)
        return self.render(request, self.list_template, kwargs)

    def create_view(self, request, **kwargs):
        kwargs['state'] = 'create'
        self.view(request, **kwargs)

    def update_view(self, request, **kwargs):
        kwargs['state'] = 'write'
        self.view(request, **kwargs)
        
    def queryset(self, request):
        return self.model.objects.all()

    def new_item(self, request):
        from keops.db import models
        r = {'pk': None}
        for field in self.model_fields:
            if field.default != models.NOT_PROVIDED:
                if callable(field.default):
                    v = field.default()
                else:
                    v = field.default
            else:
                v = None
            r[field.name] = field_text(v)
        return HttpJsonResponse(r)

    def copy(self, request):
        from keops.db import models
        self._prepare_form()
        pk = request.GET['pk']
        obj = copy.copy(self.model.objects.get(pk=pk))
        r = {'pk': None}
        for field in self.model_fields:
            if not field.primary_key and not isinstance(field, (models.ManyToManyField, models.OneToManyField)):
                r[field.name] = field_text(getattr(obj, field.name))
        return HttpJsonResponse(r)

    def get_formfield(self, field):
        if not field in self.bound_fields:
            try:
                f = self.model._meta.get_field(field)
            except:
                f = None
            if f:
                form_field = f.formfield()
                form_field.form_field = f
            else:
                lbl = field
                form_field = forms.CharField(label=lbl)
                f = getattr(self.model, field)
            self.form.fields[field] = form_field
            bound_field = self.form[field]
            form_field.target_attr = f
            self.bound_fields[field] = bound_field
        return self.bound_fields[field]

    def lookup(self, request, sel_fields=None, display_fn=str):
        """
        Read lookup data list.
        """
        from keops.views import db
        context = request.GET
        field = context.get('field')
        form_field = self.get_formfield(field).field
        queryset = form_field.queryset
        start = int(context.get('start', '0'))
        limit = int(context.get('limit', '25')) + start # settings
        query = context.get('query', '')
        fields = form_field.target_attr.custom_attrs.fields
        if query:
            queryset = db.search_text(queryset, query)
        data = {
            'data': [ field_text(obj, sel_fields=sel_fields.get(field), display_fn=display_fn) for obj in queryset[start:limit] ],
            'total': queryset.count()
        }
        return HttpJsonResponse(data)

    def delete(self, context, using):
        """
        Default delete operation.
        """
        from django.db.models.deletion import ProtectedError
        import django.db.models
        obj = self.model.objects.using(using).get(pk=context['pk'])
        try:
            obj.delete(using=using)
        except ProtectedError as e:
            return {
                'success': False,
                'action': 'DELETE',
                'label': _('Error'),
                'msg': _('Cannot delete the records because they are referenced through a protected foreign key!') + '<br>' + '<br>'.join([ capfirst(str(obj.__class__._meta.verbose_name)) + ': ' + str(obj) for obj in e.protected_objects ]),
            }
        except django.db.models.validators.ValidationError as e:
            return {
                'success': False,
                'action': 'DELETE',
                'label': _('Error'),
                'msg': '<br>'.join(e.messages),
            }

        return {
            'success': True,
            'action': 'DELETE',
            'label': _('Success'),
            'msg': _('Record successfully deleted!'),
        }

    def field_change(self, request):
        field = request.GET['field']
        f = self.model._meta.get_field(field)
        obj = self.model()
        v = json.loads(request.GET['value'])
        if f.custom_attrs.on_change:
            return HttpJsonResponse(f.custom_attrs.on_change(obj, request, field, v))

    def find_field(self, name):
        for f in self.model_fields:
            if f.name == name:
                return f

    def read(self, request):
        """
        Return JSON serialized data.
        """
        from keops.views import db
        using = db.get_db(request)
        return HttpJsonResponse(db.prepare_read(request.GET, using))

    def save(self, context, using):
        """
        Save context data on using specified database.
        """
        from keops.views import db
        from keops.db import models
        from django.db.models import ForeignKey
        pk = context.get('pk')
        if 'model' in context:
            model = context['model']
            if isinstance(model, str):
                model = db.get_model(context)
        else:
            model = self.model
        data = context.get('data')
        obj = None
        related = OrderedDict()
        if pk:
            obj = model.objects.using(using).get(pk=pk)
        if data:
            if isinstance(data, str):
                data = json.loads(data)
            obj = obj or model()
            for k, v in data.items():
                try:
                    field = model._admin.find_field(k)
                    if isinstance(field, models.DateField):
                        for format in settings.DATE_INPUT_FORMATS:
                            try:
                                v = datetime.datetime.strptime(v, format)
                                break
                            except:
                                pass
                    elif isinstance(field, ForeignKey):
                        k = field.attname
                    elif isinstance(field, models.OneToManyField):
                        related[field] = v
                        continue
                except:
                    raise
                setattr(obj, k, v)

            obj.full_clean()
            obj.save(using=using)

        # submit related data
        for field, v in related.items():
            self.save_related(field, v, obj, using)
        return True, obj

    def save_related(self, field, data, parent, using):
        """
        Save related data rows (ManyToManyField/OneToManyField).
        """
        model = field.related.model
        for obj in data:
            action = obj['action']
            record = obj['data']
            pk = record.pop('pk', None)
            if action == 'DELETE':
                model.objects.using(using).get(pk=pk).delete()
                continue
            elif action == 'CREATE':
                record[field.related.field.name] = parent.pk
            try:
                self.save({'pk': pk, 'model': model, 'data': record}, using)
            except ValidationError as e:
                raise ValidationError([str(model._meta)] + e.messages)

    def submit(self, request, **kwargs):
        """
        Receive submit data.
        """
        from keops.views import db
        using = db.get_db(request)
        if request.method == 'DELETE':
            result = self.delete(request.GET, using)
        else:
            try:
                success, obj = self.save(request.POST, using)
                result = {
                    'success': True,
                    'msg': _('Record successfully saved!'),
                    'data': db.prepare_read({'model': request.POST['model'], 'pk': obj.pk}, using)['items'][0]
                }
            except ValidationError as e:
                result = {
                    'success': False,
                    'msg': '<br>'.join(e.messages)
                }
        return HttpJsonResponse(result)
