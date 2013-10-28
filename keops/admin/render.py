from django.utils.translation import ugettext as _
from django.utils import formats
from django.utils.text import capfirst
from django import forms
from django.db import models
import keops.forms
from keops.utils.html import *
from keops.forms import widgets
from django.template import loader, RequestContext


def get_filter(field, model=None):
    try:
        if isinstance(field, str):
            field = model._meta.get_field(field)
        if isinstance(field, models.DateField):
            return '', field.name + '|date'
        elif isinstance(field, models.DecimalField):
            return ' style="text-align: right;"', field.name + '|number:2'
        else:
            return '', field.name
    except:
        pass
    return '', field


def get_field(bound_field, form):
    return loader.render_to_string('keops/forms/fields/formfield.html.mako', {
        'field': bound_field, 'forms': keops.forms, 'models': models, 'model': form.model
    })


def get_form_fields(form):
    for k, v in form.widgets.items():
        yield k, get_field(v)


def get_container(container):
    f = container[0]
    label, field = get_field(f)
    return label + TD(DIV(TABLE(TR(field, *[''.join(get_field(f)) for f in container[1:]]),
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
                f = items[idx]
                if isinstance(f, dict):
                    f = TD(TAG('fieldset', TAG('legend', f['title']), TABLE(*[TR(i) for i in f['items']])), colspan=2)
                table.append(TR(f))
            else:
                table.append(TR(TD()))
        tables.append(TABLE(*table))

    return TABLE(TR(*[TD(t, style='width: 50%') for t in tables]))


def render_form(form, cols=None, exclude=[], state=None):
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
                    f = container[0]
                    if f.name in exclude:
                        s = ''
                    else:
                        s = get_field(container[0], form)
                else:
                    s = get_container(container)
                if s:
                    fields.append(s)

    if cols is None:
        if len(items) < 6:
            cols = 1
        else:
            cols = 2
    items = get_tables(items, cols)
    if pages:
        pages = TAG('tabset', *[TAG('tab', get_tables(page['items']), heading=page['title']) for page in pages])
    else:
        pages = ''
    if state == 'write':
        attrs = {'ng-init': 'form.write=true'}
    else:
        attrs = {}
    if cols == 1:
        attrs['class'] = 'form-view1'
    else:
        attrs['class'] = 'form-view'
    items = DIV(items, pages, **attrs)
    return items
