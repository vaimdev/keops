import datetime
from collections import OrderedDict
import copy
import json
from importlib import import_module
from keops.admin import render
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.admin import options
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.template.response import TemplateResponse
from django.utils import formats
from django.utils.text import capfirst
from django.utils.encoding import force_text
from django.contrib.contenttypes import generic
from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from django.conf import settings
from django.contrib import messages
from keops.http import HttpJsonResponse, HttpMessagesResponse
from keops.utils import field_text
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
            "exclude": self.exclude,
            "formfield_callback": self.formfield_for_dbfield,
        }
        import django.forms.models
        print(self.model)
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

    def duplicate(self, request, obj):
        """
        Return model object copy.
        """
        from keops.db import models
        self._prepare_form()
        obj = copy.copy(obj)
        r = {'pk': None}
        for field in self.model_fields:
            if not field.primary_key and not isinstance(field, (models.ManyToManyField, models.OneToManyField)):
                r[field.name] = field_text(getattr(obj, field.name))
        return HttpJsonResponse(r)

    def formfield_for_dbfield(self, db_field, **kwargs):
        f = db_field.formfield(**kwargs)
        if f:
            if f.required:
                f.widget.attrs['required'] = True
            if db_field.custom_attrs.widget_attrs:
                f.widget.attrs.update(db_field.custom_attrs.widget_attrs)
            if f.help_text:
                f.widget.attrs.setdefault('tooltip', f.help_text)
                f.widget.attrs.setdefault('tooltip-trigger', 'focus')
                f.widget.attrs.setdefault('tooltip-placement', 'left')
            if db_field.readonly:
                f.widget.attrs.setdefault('readonly', True)
            elif isinstance(f, forms.DateField):
                f.widget.attrs.setdefault('class', 'form-control input-sm form-date-field')
                f.widget.attrs.setdefault('ui-mask', _('9999-99-99'))
            elif isinstance(f, forms.DecimalField):
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
        actions = super(ModelAdmin, self).get_actions(request)
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
        kwargs['form'] = self
        kwargs['opts'] = opts

        actions = self.get_actions(request)
        groups = OrderedDict()
        _cat = capfirst(_('more'))
        for k, v in actions.items():
            v = v[0]
            cat = force_text(capfirst(getattr(v, 'category', _cat)))
            if not cat in groups:
                groups[cat] = []
            groups[cat].append((k, v.__dict__))

        kwargs['action_groups'] = groups

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

    def log_addition(self, request, object):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from keops.modules.base.auth import UserLog, ADDITION
        UserLog.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=ADDITION
        )

    def log_change(self, request, object, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from keops.modules.base.auth import UserLog, CHANGE
        UserLog.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=CHANGE,
            change_message=message
        )

    def log_deletion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method is called
        before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from keops.modules.base.auth import UserLog, DELETION
        UserLog.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.model).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION
        )

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
                    field = model._admin.get_field(k)
                    if isinstance(field, models.DateField):
                        for format in settings.DATE_INPUT_FORMATS:  # TODO adjust on input widget
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
            self._save_related(field, v, obj, using)
        return True, obj

    def _save_related(self, field, data, parent, using):
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
                raise ValidationError([capfirst(field.verbose_name) + ':'] + ['%s: %s' % (capfirst(field.related.model._meta.get_field(k).verbose_name), ', '.join(v)) for k, v in e.message_dict.items()])

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
            'data': [field_text(obj, sel_fields=sel_fields.get(field), display_fn=display_fn)
                     for obj in queryset[start:limit]],
            'total': queryset.count()
        }
        return HttpJsonResponse(data)

    def new_item(self, request):
        """
        Return form with default field values.
        """
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

    def submit(self, request, **kwargs):
        """
        Receive submit data.
        """
        from keops import context
        from keops.views.db import prepare_read
        using = context.get_db(request)
        try:
            success, obj = self.save(request.POST, using)
            #self.message_user(request, obj, level=messages.SUCCESS)
            form = self.form(request.POST['data'])
            if request.POST['pk']:
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, obj, change_message)
            else:
                self.log_addition(request, obj)
            self.message_user(request, prepare_read({'model': request.POST['model'], 'pk': obj.pk}, using)['items'][0], level=messages.SUCCESS)
            self.message_user(request, _('Record successfully saved!'), level=messages.SUCCESS)
        except ValidationError as e:
            self.message_user(request, '<br>'.join(e.messages), level=messages.ERROR)
        return HttpMessagesResponse(request._messages)

    def history_view(self, request, object_id, extra_context=None):
        "The 'history' admin view for this model."
        from keops.modules.base.auth import UserLog
        # First check if the user can see this history.
        model = self.model
        obj = get_object_or_404(model, pk=unquote(object_id))

        #if not self.has_change_permission(request, obj):
        #    raise PermissionDenied

        # Then get the history for this object.
        opts = model._meta
        app_label = opts.app_label
        action_list = UserLog.objects.filter(
            object_id=unquote(object_id),
            content_type__id__exact=ContentType.objects.get_for_model(model).id
        ).select_related().order_by('action_time')

        context = {
            'title': _('Change history: %s') % force_text(obj),
            'action_list': action_list,
            'module_name': capfirst(force_text(opts.verbose_name_plural)),
            'object': obj,
            'app_label': app_label,
            'opts': opts,
            'preserved_filters': self.get_preserved_filters(request),
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.object_history_template or [
            "keops/%s/%s/object_history.html" % (app_label, opts.model_name),
            "keops/%s/object_history.html" % app_label,
            "keops/object_history.html"
        ], context, current_app=self.admin_site.name)
