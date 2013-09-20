from django.utils.translation import ugettext as _
from django.utils import formats
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django import forms
import keops.forms.fields
from keops.utils.html import *

def get_widget(field, name=None):
    d = {}
    s = {}
    if field.required:
        d['ng-required'] = 1
    if isinstance(field, forms.IntegerField):
        d['type'] = 'number'
    elif isinstance(field, forms.BooleanField):
        d['type'] = 'checkbox'
        s['ng-bind'] = 'form.item.' + name + " ? '%s': '%s'" % (capfirst(_('yes')), capfirst(_('no')))
    elif isinstance(field, forms.EmailField):
        d['type'] = 'email'
    elif isinstance(field, forms.ModelChoiceField):
        meta = field.queryset.model._meta
        d['tag'] = "input combobox"
        d['model-name'] = '%s.%s' % (meta.app_label, meta.model_name)

    if not isinstance(field, forms.BooleanField):
        d['class'] = 'char-field'
    return d, s

def get_field(name, field):
    _id = 'id-' + name
    label = LABEL(str(field.label), attrs={'for': _id})
    attrs, span = get_widget(field, name)
    tag = attrs.pop('tag', 'input')
    return TD(label, attrs={'class': 'label-cell'}), TD(
        TAG(tag=tag, id=_id, name=name, attrs={'ng-show': 'form.write', 'ng-model': 'form.item.' + name}, **attrs),
        SPAN('{{form.item.%s}}' % name, attrs={'ng-show': '!form.write'}, **span),
        attrs={'class': 'field-cell'}
    )

def get_formfields(form):
    for k, v in form.widgets.items():
        yield k, get_field(v)

def get_container(container):
    f = container[0]
    label, field = get_field(*f)
    return label + TD(DIV(TABLE(TR(field, *[''.join(get_field(*f)) for f in container[1:]]), attrs={'class': 'field-container'})), attrs={'class': 'field-cell'})

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
                    fields.append(''.join(get_field(*container[0])))
                else:
                    print('container', get_container(container))
                    fields.append(get_container(container))

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

    items = TABLE(TR(*[TD(t) for t in tables]))
    if pages:
        pages = TAG('tabset', *[TAG('tab', heading=page['title']) for page in pages])
    items = DIV(items, pages, attrs={'class': 'form-view'})
    print(items)
    return items
