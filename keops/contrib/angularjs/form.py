from django.utils.translation import ugettext as _
from django.utils import formats
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django import forms
import keops.forms.fields
from keops.utils.html import *

def get_widget(field):
    bound_field = field
    field = bound_field.field
    name = bound_field.name
    d = {}
    s = {'tag': 'span', 'ng-bind': 'form.item.' + name}
    if field.required:
        d['ng-required'] = 1
    elif isinstance(field, forms.BooleanField):
        s['ng-bind'] = 'form.item.' + name + " ? '%s': '%s'" % (capfirst(_('yes')), capfirst(_('no')))
    elif isinstance(field, forms.ModelMultipleChoiceField):
        # Adjust to show only selected values
        d['tag'] = 'div multiplechoice'
        d['options'] = '{{form.item.%s}}' % name
    elif isinstance(field, forms.ModelChoiceField):
        # Change to smart combobox widget
        meta = field.queryset.model._meta
        d['name'] = field.target_attr.attname
        d['model-name'] = '%s.%s' % (meta.app_label, meta.model_name)
        s['tag'] = 'a'
        s['ng-click'] = "openResource('%s', 'pk='%s)" % (field.target_attr.get_resource_url(), ' + form.item.%s' % field.target_attr.attname)
        s['style'] = 'cursor: pointer;'

    if not isinstance(field, forms.BooleanField):
        d['class'] = 'long-field'
    return d, s

def get_field(field):
    name = field.name
    label = field.label_tag(attrs={'class': 'field-label'})
    attrs, span = get_widget(field)
    if isinstance(field.field, forms.ModelMultipleChoiceField):
        field_args = {'colspan': 2}
        args = [label]
        label = None
    else:
        field_args = {}
        args = []
    attrs.update({'ng-show': 'form.write', 'ng-model': 'form.item.' + attrs.pop('name', name)})
    if 'tag' in attrs:
        widget = TAG(id=field.auto_id, name=name, **attrs)
    else:
        widget = field.as_widget(attrs=attrs)
    r = []
    if label:
        r = [TD(label, attrs={'class': 'label-cell'})]
    args.append(widget)
    args.append(TAG(attrs={'ng-show': '!form.write'}, **span))
    r.append(TD(attrs={'class': 'field-cell'}, *args, **field_args))
    return r

def get_form_fields(form):
    for k, v in form.widgets.items():
        yield k, get_field(v)

def get_container(container):
    f = container[0]
    label, field = get_field(f)
    return label + TD(DIV(TABLE(TR(field, *[''.join(get_field(*f)) for f in container[1:]]),
                                attrs={'class': 'field-container'})),
                      attrs={'class': 'field-cell'})

def get_tables(items, cols=2):
    l = len(items)
    c = l // cols
    c += l % cols
    tables = []
    for i in range(cols):
        table = []
        for n in range(c):
            idx = i * c + n
            if idx < l:
                table.append(TR(items[idx]))
            else:
                table.append(TR(TD()))
        tables.append(TABLE(*table))

    return TABLE(TR(*[TD(t) for t in tables]))

def form_str(form, cols=2):
    items = []
    pages = []
    for page in form:
        if page.name:
            fieldsets = []
            fsets = {'title': str(page.name), 'items': fieldsets}
            pages.append(fsets)
        else:
            fieldsets = items
        for fieldset in page:
            if fieldset.name:
                fields = []
                fs = {'title': str(fieldset.name), 'items': fields}
                fieldsets.append(fs)
            else:
                fields = fieldsets

            for container in fieldset:
                container = [f for f in container]
                if len(container) == 1:
                    fields.append(''.join(get_field(container[0])))
                else:
                    fields.append(get_container(container))

    items = get_tables(items, cols)
    if pages:
        pages = TAG('tabset', *[TAG('tab', get_tables(page['items']), heading=page['title']) for page in pages])
    else:
        pages = ''
    items = DIV(items, pages, attrs={'class': 'form-view'})
    print(items)
    return items
