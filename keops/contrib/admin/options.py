import copy
from django import forms
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.contrib.admin import options
from django.core.exceptions import (PermissionDenied, ValidationError,
    FieldError, ImproperlyConfigured, ObjectDoesNotExist)
from django.contrib import messages
from django.utils.encoding import force_text
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid, DELETION_FIELD_NAME
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.contrib.admin.utils import (unquote, flatten_fieldsets,
    get_deleted_objects, model_format_dict, NestedObjects,
    lookup_needs_distinct)
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404
from django.utils.html import escape, escapejs
from django.contrib.admin.options import IS_POPUP_VAR, TO_FIELD_VAR, add_preserved_filters, get_content_type_for_model
from django.contrib.admin.utils import lookup_field
from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE, IGNORED_PARAMS
import django.contrib.admin.views.main
from keops.db import models
from . import widgets


__all__ = ['modeladmin_factory', 'ModelAdmin']

django.contrib.admin.views.main.IGNORED_PARAMS += ('l', 't')


FORMFIELD_FOR_DBFIELD_DEFAULTS = {
    models.DateField: {'widget': widgets.AdminDateWidget},
    models.TimeField: {'widget': widgets.AdminTimeWidget},
    models.TextField: {'widget': widgets.AdminTextareaWidget},
    models.URLField: {'widget': widgets.AdminURLFieldWidget},
    models.IntegerField: {'widget': widgets.AdminIntegerFieldWidget},
    models.BigIntegerField: {'widget': widgets.AdminBigIntegerFieldWidget},
    models.CharField: {'widget': widgets.AdminTextInputWidget},
    models.ImageField: {'widget': widgets.AdminFileWidget},
    models.FileField: {'widget': widgets.AdminFileWidget},
    models.EmailField: {'widget': widgets.AdminEmailInputWidget},
    models.BooleanField: {'widget': forms.CheckboxInput},
}


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


class ModelAdmin(options.ModelAdmin):
    title = None
    help_text = ''

    def __init__(self, model, admin_site):
        self._orig_formfield_overrides = self.formfield_overrides
        super(ModelAdmin, self).__init__(model, admin_site)
        self.formfield_overrides = FORMFIELD_FOR_DBFIELD_DEFAULTS.copy()
        self.formfield_overrides.update(self._orig_formfield_overrides)
        if not self.title:
            self.title = model._meta.verbose_name_plural

    def db_list(self, request):
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = self.get_search_fields(request)

        ChangeList = self.get_changelist(request)
        cl = ChangeList(request, self.model, list_display,
            list_display_links, list_filter, self.date_hierarchy,
            search_fields, self.list_select_related, self.list_per_page,
            self.list_max_show_all, self.list_editable, self)
        q = cl.get_queryset(request)
        r = []
        for obj in q:
            row = {'pk': obj.pk}
            for field_name in cl.list_display:
                try:
                    f, attr, value = lookup_field(field_name, obj, cl.model_admin)
                except ObjectDoesNotExist:
                    result_repr = EMPTY_CHANGELIST_VALUE
                    row[field_name] = result_repr
                else:
                    row[field_name] = value
            r.append(row)
        return JsonResponse({'items': r})

    def db_read(self, request):
        try:
            p = request.GET.get('p')
            pk = request.GET.get('pk')
            if p:
                obj = self.model.objects.all()[int(p)]
            elif pk:
                obj = self.model.objects.get(pk=request.GET.get('pk'))
            data = {'pk': obj.pk}
            if not self.fields:
                self.fields = ['name']
            for f in self.fields:
                data[f] = lookup_field(f, obj, self)[2]
            data = [data]
        except:
            raise
            data = {}
        return JsonResponse({'items': data})

    def render(self, request, view_type, *args, **kwargs):
        if view_type == 'list':
            return self.changelist_view(request, *args, **kwargs)
        elif view_type == 'form':
            return self.changeform_view(request, *args, **kwargs)

    @options.csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        The 'change list' admin view for this model.
        """
        opts = self.model._meta
        app_label = opts.app_label

        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = self.get_search_fields(request)

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        if actions:
            # Add the action checkboxes if there are any actions available.
            list_display = ['action_checkbox'] + list(list_display)

        ChangeList = self.get_changelist(request)
        cl = ChangeList(request, self.model, list_display,
            list_display_links, list_filter, self.date_hierarchy,
            search_fields, self.list_select_related, self.list_per_page,
            self.list_max_show_all, self.list_editable, self)

        cl.formset = None

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        if actions:
            # Add the action checkboxes if there are any actions available.
            list_display = ['action_checkbox'] + list(list_display)

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else:
            action_form = None

        context = dict(
            self.admin_site.each_context(),
            model_admin=self,
            cl=cl,
            module_name=force_text(opts.verbose_name_plural),
            has_add_permission=self.has_add_permission(request),
            action_form=action_form,
            opts=opts,
        )
        context.update(extra_context or {})

        return TemplateResponse(request, self.change_list_template or [
            'keops/%s/%s/change_list.html' % (app_label, opts.model_name),
            'keops/%s/change_list.html' % app_label,
            'keops/change_list.html'
        ], context, current_app=self.admin_site.name)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)
        view_on_site_url = self.get_view_on_site_url(obj)
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,  # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': view_on_site_url is not None,
            'absolute_url': view_on_site_url,
            'form_url': form_url,
            'opts': opts,
            'content_type_id': get_content_type_for_model(self.model).pk,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'to_field_var': TO_FIELD_VAR,
            'is_popup_var': IS_POPUP_VAR,
            'app_label': app_label,
        })
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.change_form_template

        return TemplateResponse(request, form_template or [
            "keops/%s/%s/change_form.html" % (app_label, opts.model_name),
            "keops/%s/change_form.html" % app_label,
            "keops/change_form.html"
        ], context, current_app=self.admin_site.name)

    @options.csrf_protect_m
    @options.transaction.atomic
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        model = self.model
        opts = model._meta
        add = object_id is None
        obj = None

        if False:
            if add:
                if not self.has_add_permission(request):
                    raise PermissionDenied
                obj = None

            else:
                obj = self.get_object(request, unquote(object_id))

                if not self.has_change_permission(request, obj):
                    raise PermissionDenied

                if obj is None:
                    raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                        'name': force_text(opts.verbose_name), 'key': escape(object_id)})

                if request.method == 'POST' and "_saveasnew" in request.POST:
                    return self.add_view(request, form_url=reverse('admin:%s_%s_add' % (
                        opts.app_label, opts.model_name),
                        current_app=self.admin_site.name))

        ModelForm = self.get_form(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=not add)
            else:
                form_validated = False
                new_object = form.instance
            formsets, inline_instances = self._create_formsets(request, new_object)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                if add:
                    self.log_addition(request, new_object)
                    return self.response_add(request, new_object)
                else:
                    change_message = self.construct_change_message(request, form, formsets)
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
        else:
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(request, self.model())
            else:
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(request, obj)

        adminForm = options.helpers.AdminForm(
            form,
            list(self.get_fieldsets(request, obj)),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        context = dict(self.admin_site.each_context(),
            title=self.title,
            adminform=adminForm,
            object_id=object_id,
            original=obj,
            is_popup=(options.IS_POPUP_VAR in request.POST or
                      options.IS_POPUP_VAR in request.GET),
            to_field=request.POST.get(options.TO_FIELD_VAR,
                                      request.GET.get(options.TO_FIELD_VAR)),
            media=media,
            inline_admin_formsets=inline_formsets,
            errors=options.helpers.AdminErrorList(form, formsets),
            preserved_filters=self.get_preserved_filters(request),
        )

        context.update(extra_context or {})

        return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        request = kwargs.pop("request", None)

        # If the field specifies choices, we don't need to look for special
        # admin widgets - we just need to use a select widget of some kind.
        if db_field.choices:
            # see #19303 for an explanation of self._orig_formfield_overrides
            if db_field.__class__ in self._orig_formfield_overrides:
                kwargs = dict(self._orig_formfield_overrides[db_field.__class__], **kwargs)
            formfield = self.formfield_for_choice_field(db_field, request, **kwargs)
            formfield.widget = widgets.ChoiceFieldWidgetWrapper(formfield.widget)
            return formfield

        # ForeignKey or ManyToManyFields
        if isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            # Combine the field kwargs with any options for formfield_overrides.
            # Make sure the passed in **kwargs override anything in
            # formfield_overrides because **kwargs is more specific, and should
            # always win.
            if db_field.__class__ in self.formfield_overrides:
                kwargs = dict(self.formfield_overrides[db_field.__class__], **kwargs)

            # Get the correct formfield.
            if isinstance(db_field, models.ForeignKey):
                formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)
            elif isinstance(db_field, models.ManyToManyField):
                formfield = self.formfield_for_manytomany(db_field, request, **kwargs)

            # For non-raw_id fields, wrap the widget with a wrapper that adds
            # extra HTML -- the "add other" interface -- to the end of the
            # rendered output. formfield can be None if it came from a
            # OneToOneField with parent_link=True or a M2M intermediary.
            if formfield and db_field.name not in self.raw_id_fields:
                related_modeladmin = self.admin_site._registry.get(db_field.rel.to)
                can_add_related = bool(related_modeladmin and
                    related_modeladmin.has_add_permission(request))
                formfield.widget = widgets.RelatedFieldWidgetWrapper(
                    formfield.widget, db_field.rel, self.admin_site,
                    can_add_related=can_add_related)

            return formfield

        # If we've got overrides for the formfield defined, use 'em. **kwargs
        # passed to formfield_for_dbfield override the defaults.
        for klass in db_field.__class__.mro():
            if klass in self.formfield_overrides:
                kwargs = dict(copy.deepcopy(self.formfield_overrides[klass]), **kwargs)
                return db_field.formfield(**kwargs)

        # For any other type of field, just call its formfield() method.
        return db_field.formfield(**kwargs)


def modeladmin_factory(model, **options):
    admin = getattr(model._meta, 'Admin', None)
    if admin:
        admin = {k: v for k, v in admin.__dict__.items() if not k.startswith('_')}
    else:
        admin = {}
    admin.update(options)
    admin['model'] = model
    return type(model.__name__ + 'Admin', (ModelAdmin,), admin)
