from collections import OrderedDict
import json
from django.utils import six
from django import forms
from keops.utils.html import *
from keops.contrib.angularjs import form
from .forms import View

class FieldLine(object):
    def __init__(self, form, fields):
        self.form = form
        self.fields = fields
    
    def __iter__(self):
        for field in self.fields:
            yield (field, self.form.get_formfield(field))

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
        if attrs.get('admin_default', None):
            new_class()
        return new_class
            
class ModelAdmin(six.with_metaclass(ModelAdminBase, View)):
    admin_default = False
    template_name = 'keops/forms/model_form.html'
    list_template = 'keops/forms/list_form.html'
    fields = ()
    exclude = ()
    readonly_fields = ()
    list_display = ()
    pages = ()
    search_fields = ()
    columns = 2
    form_fields = {}
    bound_fields = {}
    formfield_overrides = None

    toolbar_actions = ['create', 'read', 'update', 'delete', 'print', 'delete', 'search']

    actions = []
    model = None
    title = None
    label = None
    help_text = ''

    def __init__(self, admin=None):
        self.admin = admin
        self._prepared = False
        self._form = None
        self._instance = None
        if self.model:
            if self.admin_default:
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
        from django.contrib.contenttypes import generic
        extra = getattr(self.model, 'Extra', None)
        if extra:
            if not self.fields and extra.field_groups and extra.field_groups.get('display_fields', None):
                self.fields = extra.field_groups['display_fields']
            if not self.list_display and extra.field_groups and extra.field_groups.get('list_fields', None):
                self.list_display = extra.field_groups['list_fields']
        if self.model._meta.abstract:
            return
        from django.db import models
        model_fields = self.model._meta.concrete_fields + self.model._meta.many_to_many + self.model._meta.virtual_fields
        self.model_fields = model_fields
        if not self.fields:
            self.fields = [f.name for f in model_fields if not f.name in self.exclude and not isinstance(f, (
                models.AutoField, generic.GenericForeignKey)) and\
                getattr(f, 'custom_attrs', {}).get('visible', not f.primary_key)]
        if not self.list_display:
            self.list_display = [f.name for f in self.model._meta.concrete_fields if not f.name in self.exclude and not\
                isinstance(f, (models.AutoField, models.ManyToManyField)) and\
                getattr(f, 'custom_attrs', {}).get('visible', not f.primary_key)]

        if not self.pages:
            pages = OrderedDict()

        for field in model_fields:
            if not field.name in self.fields:
                continue
            if not self.pages:
                attrs = getattr(field, 'custom_attrs', {})
                page = pages.setdefault(str(attrs.get('page', None) or ''), OrderedDict())
                fieldset = page.setdefault(str(attrs.get('fieldset', None) or ''), {'fields': []})
                fieldset['fields'].append(field.name)

        if not self.pages and pages:
            for page, fieldsets in pages.items():
                pages[page] = tuple(fieldsets.items())
            self.pages = tuple(pages.items())

        if self.search_fields:
            # set search field to __icontains
            for i, f in enumerate(self.search_fields):
                if not '__' in f:
                    self.search_fields[i] = '%s__icontains' % f
        elif not self.search_fields or not self.display_expression:
            search_fields = ''
            for f in self.fields:
                field = self.model._meta.get_field(f)
                if isinstance(field, models.CharField):
                    search_fields = ['%s__icontains']
                    break
            self.search_fields = self.search_fields or search_fields or (self.fields and [self.fields[0]]) or ()
            
        self.title = self.title or self.model._meta.verbose_name_plural
        self.label = self.label or self.model._meta.verbose_name

    def _prepare_form(self):
        if self._prepared:
            return
        self._prepare()
        for field in self.model_fields:
            if not field.name in self.fields:
                continue
            if not field.name in self.form_fields:
                f = getattr(field, 'custom_attrs', {}).get('widget', None) or field.formfield()
                self.form_fields[field.name] = f
                f.target_attr = field
                return f
        self._prepared = True

    def __iter__(self):
        self._prepare_form()
        for page, fieldsets in self.pages:
            yield TabPage(page, self, fieldsets)

    def as_table(self):
        s = TABLE()
        return

    @property
    def form(self):
        if not self._form:
            self._form = forms.models.modelform_factory(self.model)
        return self._form

    def _prepare_context(self, request, context):
        context.update({
            'model': self.model,
            'model_name': '%s.%s' % (self.model._meta.app_label, self.model._meta.model_name),
        })
        
    def view(self, request, view_type, **kwargs):
        if view_type == 'list':
            v = self.list_view
        else:
            self._prepare_change_view(request, kwargs)
            v = super(ModelAdmin, self).view
        return v(request, **kwargs)
    
    def _prepare_change_view(self, request, context):
        context['form_view'] = form.form_str(self)
        pk = request.GET.get('pk')
        if pk:
            context['pk'] = pk
        self._prepare_context(request, context)

    def list_view(self, request, **kwargs):
        self._prepare_form()
        kwargs['query'] = request.GET.get('query', '')
        kwargs['fields'] = [self.get_formfield(f) for f in self.list_display]
        kwargs['list_display'] = ['{{item.%s}}' % f for f in self.list_display]
        self._prepare_context(request, kwargs)
        kwargs.setdefault('pagesize', 50)
        return self.render(request, self.list_template, kwargs)

    def add_view(self, request, **kwargs):
        kwargs['state'] = 'create'
        self.view(request, **kwargs)

    def edit_view(self, request, **kwargs):
        kwargs['state'] = 'write'
        self.view(request, **kwargs)
        
    def get_queryset(self, request):
        return self.model.objects.all()

    def get_formfield(self, field):
        self._prepare_form()
        if not field in self.form_fields:
            f = self.model._meta.get_field(field)
            if f:
                w = f.formfield()
                w.form_field = f
                self.form_fields[field] = w
                lbl = w.label
            else:
                lbl = field
                w = forms.CharField(label=lbl)
                f = getattr(self.model, field)
            w.target_attr = f
            self.form_fields[field] = w
        return self.form_fields[field]
