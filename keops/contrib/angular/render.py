from django.utils.translation import ugettext as _
from django.utils import formats
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django import forms
from django.db import models
import django.forms.widgets
import keops.forms
from keops.utils.html import *
from keops.forms import widgets
from django.template import loader, Context

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

def get_field(bound_field, form, exclude=[], state=None):

    if bound_field.name in exclude:
        return []

    field = bound_field.field
    name = bound_field.name
    readonly = name in form.readonly_fields

    widget_attrs = field.widget.attrs.copy()
    widget_attrs.update(field.target_attr.custom_attrs.get('widget_attrs', {}))
    widget_attrs.update({'ng-model': 'form.item.' + name, 'ng-show': 'form.write'})
    if readonly:
        span = '<span ng-show="!form.write || form.readonly.%s" ng-bind="form.item.%s"></span>' % (name, name)
        widget_attrs['ng-show'] += ' && !form.readonly.%s' % name
    else:
        span = '<span ng-show="!form.write" ng-bind="form.item.%s"></span>' % name
    widget = ''
    label = bound_field.label_tag(attrs={'class': 'form-field-label'}, label_suffix=' ')
    cell_attrs = {'class': 'form-field-cell'}

    attrs = {}


    if isinstance(field, forms.BooleanField):
        widget = '<label style="cursor: pointer" ng-show="!form.write">%s</label>' % forms.widgets.CheckboxInput(attrs=widget_attrs).render(name, None)
        span = '<span ng-show="!form.write || form.readonly.%s" ng-bind="form.item.%s ? \'%s\': \'%s\'"></span>' % (name, name, capfirst(_('yes')), capfirst(_('no')))
    elif isinstance(field, forms.DateTimeField):
        span = '<span ng-show="!form.write || form.readonly.%s">{{form.item.%s | dateFromNow}}</span>' % (name, name)
    elif isinstance(field, forms.DateField):
        span = '<span ng-show="!form.write || form.readonly.%s">{{form.item.%s | dateFrom}}</span>' % (name, name)
    elif isinstance(field, forms.EmailField):
        span = '<a ng-href="mailto:{{form.item.%s}}" ng-show="!form.write || form.readonly.%s"></a>' % (name, name)
    elif isinstance(field, forms.ModelMultipleChoiceField):
        pass
        # TODO user select2
    elif isinstance(field, keops.forms.GridField):
        cell_attrs = {'colspan': 2, 'style': 'width: 100%;'}
        span = ''

        widget = '<div remoteitem style="max-height: 200px; overflow: auto;" name="%s">' % name
        model = field.target_attr.related.model
        related = field.target_attr.related
        list_fields = field.target_attr.list_fields
        attrs = {'class': 'grid-field', 'style': 'table-layout: inherit;'}
        attrs.update(field.target_attr.custom_attrs.get('widget_attrs', {}))
        model_name = field.target_attr.model._meta.app_label + '.' + field.target_attr.model._meta.model_name
        fields = [ model._meta.get_field(f) for f in list_fields if related.field.name != f ]
        head = [ '<th%s>%s</th>' % (get_filter(f)[0], capfirst(f.verbose_name)) for f in fields ] + [TH('', style='width: 10px;')]
        cols = [ '<td%s>{{item.%s}}</td>' % (((isinstance(f, models.ForeignKey) or f.choices) and ('', f.name + '.text')) or get_filter(f)) for f in fields ] +\
            [TD('<i ng-show="form.write" style="cursor: pointer" title="%s" class="icon-remove"></i>''' % capfirst(_('remove item')), style='padding-right: 5px;')]

        widget += bound_field.label_tag(
            attrs={'class': 'field-label', 'style': 'display: inline-block; padding-right: 10px;'},
            label_suffix=' '
        )
        widget += TAG('a', capfirst(_('add')),
            attrs={'ng-show': 'form.write', 'class': 'btn', 'ng-click': "showDetail('%s', '%s')" % (model_name, name)}
        )
        widget += TAG('table ui-table ng-model=\'%s\'' % name,
                THEAD(
                    TR(*head)
                ),
                TBODY(
                    TR(
                        attrs={
                            'ui-table-row': 'ui-table.row',
                            'ng-repeat': 'item in form.item.' + name,
                            'ng-click': "form.write && showDetail('%s', '%s', item)" % (model_name, name)},
                        *cols
                    )
                ),
                attrs=attrs
        )
        widget += '</div>'
        label = ''

    elif isinstance(field, forms.ModelChoiceField):
        url = field.target_attr.get_resource_url()
        if url:
            span = '<a style="cursor: pointer" ng-show="!form.write" ng-bind="form.item.%s.text" ng-click="openResource(\'%s\', \'pk=\' + form.item.%s.id, %s)"></a>' % (name, url, name, name)
        else:
            span = '<a ng-show="!form.write" ng-bind="form.item.%s.text"></a>' % name

        widget_attrs.update({
            'lookup-url': '/db/lookup/?model=%s.%s&field=%s' % (
                field.target_attr.model._meta.app_label,
                field.target_attr.model._meta.model_name,
                name,
            )
        })
        widget = '<div ng-show="%s" class="form-long-field">' % (widget_attrs.pop('ng-show'))
        widget += TAG('input combobox type="hidden" id="%s"' % bound_field.auto_id,
            **widget_attrs
        )
        widget += '</div>'
        cell_attrs['style'] = 'padding-right: 10px; max-width: 1px;' # adjust select2 size
    elif isinstance(field, forms.ChoiceField):
        span = '<span ng-show="!form.write || form.readonly.%s" ng-bind="form.item.%s.text"></span>' % (name, name)
        cell_attrs['style'] = 'padding-right: 0;'
    elif isinstance(field.widget, widgets.widgets.Textarea):
        widget_attrs['style'] = 'height: 70px; margin: 0; resize: none;'
        span = '<span ng-show="!form.write || form.readonly.%s" ng-bind="form.item.%s" class="text-field-span"></span>' % (name, name)
    elif isinstance(field, forms.DecimalField):
        widget_attrs['ui-money-thousands'] = formats.get_format('THOUSAND_SEPARATOR')
        widget_attrs['ui-money-decimal'] = formats.get_format('DECIMAL_SEPARATOR')
        widget_attrs['ui-money-negative'] = True
        widget_attrs['id'] = bound_field.auto_id

        widget = TAG('input ui-money', attrs=widget_attrs)

        span = '<span ng-show="!form.write || form.readonly.%s">{{form.item.%s | number:2}}</span>' % (name, name)

    if readonly:
        cell_attrs['ng-init'] = 'form.readonly.%s = true' % name

    if not widget:
        widget = bound_field.as_widget(attrs=widget_attrs)

    r = []
    if label:
        r = [TD(label, attrs={'class': 'form-label-cell'})]

    if state != 'write':
        widget += span
    r.append(TD(widget, **cell_attrs))
    return r

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
                    s = ''.join(get_field(container[0], form, exclude, state))
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
