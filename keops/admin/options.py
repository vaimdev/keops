from collections import OrderedDict
from importlib import import_module
from keops.admin import render
from django.contrib.admin import options
from django.template.response import TemplateResponse
from django.utils import formats
from django.contrib.contenttypes import generic
from django.db import models
from django import forms
from keops.http import HttpJsonResponse
from .reports import ReportLink, Reports


__all__ = ['modeladmin_factory', 'ModelAdmin']


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


def modeladmin_factory(cls, model):
    if cls:
        data = {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}
    else:
        data = {}
    return type(model.__name__ + 'Admin', (ModelAdmin,), data)


class ModelAdmin(options.ModelAdmin):
    _bound_form = None
    _prepared = False
    print_fields = ()
    reports = ()
    pages = ()
    use_form_actions = True  # If base.formaction objects are allowed
    bound_fields = {}
    title = None
    label = None
    help_text = None

    def __iter__(self):
        for page, fieldsets in self.pages:
            yield TabPage(page, self, fieldsets)

    def __get__(self, instance, owner):
        self._prepare_form()
        return self

    def _prepare(self):
        """
        Prepare admin with model data dict.
        """
        if self._prepared:
            return

        list_display = self.list_display
        if list_display is options.ModelAdmin.list_display:
            list_display = None

        # Load data dict by model Extra class
        extra = getattr(self.model, 'Extra', None)
        if extra:
            if not self.fields and extra.field_groups and extra.field_groups.get('display_fields', None):
                self.fields = extra.field_groups['display_fields']

            if not list_display and extra.field_groups and extra.field_groups.get('list_fields', None):
                list_display = extra.field_groups['list_fields']

            if not self.print_fields and extra.field_groups and extra.field_groups.get('print_fields', None):
                self.print_fields = extra.field_groups['print_fields']

            if not self.reports and getattr(extra, 'reports', None):
                self.reports = Reports([ReportLink(report, import_module(self.model.__module__)) for report in extra.reports])

        if self.model._meta.abstract:
            return

        model_fields = self.model._meta.all_fields
        self.model_fields = model_fields

        if not self.fields:
            self.fields = [f.name for f in model_fields if not f.name in (self.exclude or []) and not isinstance(f, (
                models.AutoField, generic.GenericForeignKey)) and
                f.custom_attrs.get('visible', not f.primary_key)]

        if list_display:
            self.list_display = list_display
        else:
            self.list_display = [f.name for f in self.model._meta.all_fields if not f.name in self.exclude and not
                isinstance(f, (models.AutoField, models.ManyToManyField)) and
                f.custom_attrs.get('visible', not f.primary_key)]

        if not self.print_fields:
            self.print_fields = self.list_display

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
            # set default search field to __icontains
            for i, f in enumerate(self.search_fields):
                if not '__' in f:
                    self.search_fields[i] = '%s__icontains' % f
        elif not self.search_fields or not self.display_expression:
            search_fields = []
            for f in self.model_fields:
                try:
                    # FIND ONLY DB CHAR FIELDS
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

        defaults = {
            "form": self.form,
            "fields": self.fields,
            "exclude": self.exclude,
            "formfield_callback": self.formfield_for_dbfield,
        }
        import django.forms.models
        self.form = django.forms.models.modelform_factory(self.model, **defaults)
        self.bound_fields = {}

    def _prepare_form(self):
        self._prepare()
        for name in self.fields:
            field = self.get_field(name)
            if field and not name in self.bound_fields:
                self.get_formfield(name)

        self._prepared = True

    @property
    def bound_form(self):
        if not self._bound_form:
            self._bound_form = self.form()
        return self._bound_form

    def contribute_to_class(self, cls, name):
        cls._admin = self
        self.model = cls

    def formfield_for_dbfield(self, db_field, **kwargs):
        f = db_field.formfield(**kwargs)
        if f:
            if db_field.custom_attrs.widget_attrs:
                f.widget.attrs.update(db_field.custom_attrs.widget_attrs)
            if f.help_text:
                f.widget.attrs.setdefault('tooltip', f.help_text)
            if db_field.readonly:
                f.widget.attrs.setdefault('readonly', True)
            elif isinstance(f, forms.DateField):
                f.widget.attrs.setdefault('class', 'form-control input-sm form-date-field')
                f.widget.attrs.setdefault('ui-mask', _('9999-99-99'))
            elif isinstance(f, forms.DecimalField):
                f.widget.attrs['type'] = 'text'
                f.widget.attrs['ui-money'] = 'ui-money'
                f.widget.attrs['ui-money-thousands'] = formats.get_format('THOUSAND_SEPARATOR')
                f.widget.attrs['ui-money-decimal'] = formats.get_format('DECIMAL_SEPARATOR')
                f.widget.attrs['ui-money-negative'] = True
                f.widget.attrs.setdefault('class', 'form-control input-sm form-decimal-field')
            elif isinstance(f, forms.IntegerField):
                f.widget.attrs.setdefault('class', 'form-control input-sm form-int-field')
            elif isinstance(f, forms.CharField) and f.max_length and f.max_length <= 5:
                f.widget.attrs.setdefault('class', 'form-control input-sm form-5c-field')
            elif isinstance(f, forms.CharField) and f.max_length and f.max_length <= 15:
                f.widget.attrs.setdefault('class', 'form-control input-sm form-small-field')
            elif isinstance(f, forms.CharField) and f.max_length and f.max_length <= 20:
                f.widget.attrs.setdefault('class', 'form-control input-sm form-20c-field')
            elif isinstance(f.widget, forms.Textarea):
                f.widget.attrs.setdefault('style', 'resize: none; height: 70px;')
                f.widget.attrs.setdefault('class', 'form-control input-sm form-long-field')
            elif isinstance(f, forms.CharField):
                f.widget.attrs.setdefault('class', 'form-control input-sm form-long-field')
            return f

    def get_actions(self, request):
        """
        Return all admin actions.
        """
        actions = super(self.get_actions())
        # Add form_actions
        if self.use_form_actions:
            actions.update(self.get_form_actions(request))
        return actions

    def get_field(self, field):
        for f in self.model_fields:
            if f.name == field:
                return f

    def get_form_actions(self, request):
        """
        Return all base.formaction actions.
        """
        from django.contrib.contenttypes.models import ContentType
        from keops.modules.base.models import FormAction
        ct = ContentType.objects.get_by_natural_key(self.model._meta.app_label, self.model._meta.model_name)
        actions = FormAction.objects.filter(content_type=ct, is_admin=True)
        r = OrderedDict()
        for action in actions:
            r[action.pk] = action
        return r

    def get_formfield(self, field):
        if not field in self.bound_fields:
            try:
                f = self.get_field(field)
            except:
                f = None
            if f:
                form_field = self.formfield_for_dbfield(f)
            else:
                lbl = field
                form_field = forms.CharField(label=lbl)
                f = getattr(self.model, field)
            self.bound_form.fields[field] = form_field
            bound_field = self.bound_form[field]
            form_field.target_attr = f
            self.bound_fields[field] = bound_field
        return self.bound_fields[field]

    def read(self, request):
        """
        Return JSON serialized data.
        """
        from keops.views import db
        using = db.get_db(request)
        return HttpJsonResponse(db.prepare_read(request.GET, using))

    def view(self, request, view_type, **kwargs):
        self._prepare_form()
        opts = self.model._meta
        app_label = opts.app_label
        kwargs['opts'] = opts

        if view_type == 'list':
            list_display = self.get_list_display(request)
            list_filter = self.get_list_filter(request)


            kwargs['query'] = request.GET.get('query', '')
            kwargs['fields'] = [(render.get_filter(f, self.model)[0], self.get_formfield(f).label)
                                for f in self.list_display]
            kwargs['list_display'] = ['<td%s>{{item.%s}}</td>' % render.get_filter(f, self.model)
                                      for f in self.list_display]
            kwargs.setdefault('pagesize', 50)

            return TemplateResponse(request, self.change_list_template or [
                'keops/%s/%s/change_list.html' % (app_label, opts.model_name),
                'keops/%s/change_list.html' % app_label,
                'keops/change_list.html'
            ], kwargs, current_app=self.admin_site.name)
        else:
            kwargs['form_view'] = render.render_form(self)
            pk = request.GET.get('pk')
            if pk:
                kwargs['pk'] = pk
            return TemplateResponse(request, self.change_form_template or [
                "keops/%s/%s/change_form.html" % (app_label, opts.model_name),
                "keops/%s/change_form.html" % app_label,
                "keops/change_form.html"
            ], kwargs, current_app=self.admin_site.name)
