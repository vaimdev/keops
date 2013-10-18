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

def get_field(field, form=None, exclude=[], state=None):
    bound_field = field
    field = bound_field.field
    name = bound_field.name
    if name in exclude:
        return []
    attrs = {'ng-model': 'form.item.' + name, 'ng-show': 'form.write'}
    span = {'ng-bind': 'form.item.' + name}
    widget_args = []
    label = bound_field.label_tag(attrs={'class': 'field-label'}, label_suffix=' ')
    args = []
    span_args = []
    field_args = {'class': 'field-cell'}
    span_tag = 'span'

    readonly = name in form.readonly_fields

    if field.required:
        attrs['required'] = 1

    if isinstance(field, (forms.DateField, forms.IntegerField)) or (isinstance(field, forms.CharField) and field.max_length and field.max_length < 10):
        attrs['class'] = 'small-field'
    elif isinstance(field, forms.DateTimeField) or (isinstance(field, forms.CharField) and field.max_length and field.max_length <= 15):
        attrs['class'] = 'normal-field'
    elif isinstance(field, forms.CharField) and field.max_length and field.max_length <= 20:
        attrs['class'] = 'normal-20c-field'
    else:
        attrs['class'] = 'long-field'

    if isinstance(field, forms.BooleanField):
        attrs = {'tag': 'label', 'ng-show': attrs.pop('ng-show'), 'style': 'cursor: pointer;'}
        widget_args = [TAG('input type="checkbox"', ngModel='form.item.' + name, id=bound_field.auto_id)]
        span['ng-bind'] = "form.item.%s ? '%s': '%s'" % (name, capfirst(_('yes')), capfirst(_('no')))
    elif isinstance(field, forms.DateTimeField):
        span_args.append('{{%s | dateFromNow}}' % span.pop('ng-bind'))
    elif isinstance(field, forms.DateField):
        span_args.append('{{%s | dateFrom}}' % span.pop('ng-bind'))
    elif isinstance(field, forms.EmailField):
        span_tag = 'a'
        span['ng-href'] = 'mailto:{{form.item.%s}}' % name
    elif field.target_attr.choices:
        span['ng-bind'] = 'form.item.%s.text' % name
    elif isinstance(field, forms.ModelMultipleChoiceField):
        attrs['tag'] = 'div remoteitem'
        attrs['name'] = name
        field_args = {'colspan': 2}
        args = [
            bound_field.label_tag(
                attrs={'style': 'display: inline-block; padding-right: 10px;', 'class': 'field-label'},
                label_suffix=' '
            ),
            '<a style="display: inline-block" ng-show="form.write" class="btn">%s</a>' % capfirst(_('add')),
        ]
        label = None
        bind = 'item.__str__'
        attrs.pop('ng-show')
        args.append(
            DIV(
                LABEL(
                    '''<a style="cursor: pointer;" ng-bind="%s"></a>
                    <i ng-show="form.write" title="%s" style="margin-left: 10px; cursor: pointer;" class="icon-remove"></i>''' % (bind, capfirst(_('remove item'))),
                    attrs={'class': 'multiplechoice-item', 'ng-repeat': 'item in form.item.' + name}),
                attrs={'class': 'grid-field'}
            )
        )

        span = {}
        span_args = []
        span_tag = None
    elif isinstance(field, keops.forms.GridField):
        field_args = {'colspan': 2, 'style': 'width: 100%;'}

        attrs['tag'] = 'table remoteitem'
        attrs['name'] = name
        attrs.pop('ng-show')
        span['ng-bind'] = 'item.__str__'
        model = field.target_attr.related.model
        related = field.target_attr.related
        list_fields = field.target_attr.list_fields
        model_name = field.target_attr.model._meta.app_label + '.' + field.target_attr.model._meta.model_name
        fields = [ model._meta.get_field(f) for f in list_fields if related.field.name != f ]
        head = [ '<th%s>%s</th>' % (get_filter(f)[0], capfirst(f.verbose_name)) for f in fields ] + [TH('', style='width: 10px;')]
        cols = [ '<td%s>{{item.%s}}</td>' % (((isinstance(f, models.ForeignKey) or f.choices) and ('', f.name + '.text')) or get_filter(f)) for f in fields ] +\
            [TD('<i ng-show="form.write" style="cursor: pointer" title="%s" class="icon-remove"></i>''' % capfirst(_('remove item')), style='padding-right: 5px;')]
        widget_args = [
            TABLE(
                THEAD(
                    TR(*head)
                ),
                TBODY(
                    TR(
                        attrs={'ng-repeat': 'item in form.item.' + name, 'ng-click': 'showDetail(\'%s\', \'%s\', item)' % (model_name, name)},
                        *cols
                    )
                ),
                attrs={'class': 'grid-field', 'style': 'table-layout: inherit;'}
            )
        ]

        args = [
            bound_field.label_tag(
                attrs={'class': 'field-label', 'style': 'display: inline-block; padding-right: 10px;'},
                label_suffix=' '
            ),
            TAG('a', capfirst(_('add')),
                attrs={'ng-show': 'form.write', 'class': 'btn', 'ng-click': 'showDetail(\'%s\', \'%s\')' % (model_name, name)}
            )
        ]
        label = None
        span = {}
        span_args = []
        span_tag = None
    elif isinstance(field, forms.ModelChoiceField):
        widget_args.append(
            TAG('input combobox type="hidden" ng-model="%s" id="%s"' % (attrs.pop('ng-model'), bound_field.auto_id),
                **{
                    'class': attrs.get('class'),
                    'lookup-url': '/db/lookup/?model=%s.%s&field=%s' %
                                  (field.target_attr.model._meta.app_label,
                                   field.target_attr.model._meta.model_name,
                                   name)}))
        attrs = {'tag': 'div', 'ng-show': 'form.write'}
        span['ng-bind'] += '.text'
        # Change to remote combobox widget
        span_tag = 'a'
        url = field.target_attr.get_resource_url()
        if url:
            span['ng-click'] = "openResource('%s', 'pk='%s)" % (url, ' + form.item.%s.id' % name)
        span['style'] = 'cursor: pointer;'
    elif isinstance(field.widget, widgets.widgets.Textarea):
        attrs['style'] = 'height: 70px; margin: 0; resize: none;'
    elif isinstance(field, forms.DecimalField):
        attrs['tag'] = 'input ui-money'
        attrs['ui-money-thousands'] = formats.get_format('THOUSAND_SEPARATOR')
        attrs['ui-money-decimal'] = formats.get_format('DECIMAL_SEPARATOR')
        attrs['ui-money-negative'] = True
        attrs['id'] = bound_field.auto_id
        span_args.append('{{%s | number:2}}' % span.pop('ng-bind'))

    if readonly:
        attrs['ng-init'] = 'form.readonly.%s = true' % name
        if 'ng-show' in attrs:
            attrs['ng-show'] += ' && !form.readonly.%s' % name

    if 'tag' in attrs:
        widget = TAG(attrs.pop('tag'), name=attrs.pop('name', None) or name, *widget_args, **attrs)
    else:
        widget = bound_field.as_widget(attrs=attrs)

    r = []
    if label:
        r = [TD(label, attrs={'class': 'label-cell'})]
    args.append(widget)
    if state != 'write':
        if span_tag:
            args.append(TAG(span_tag, attrs={'ng-show': '!form.write || form.readonly.' + name}, *span_args, **span))
    r.append(TD(*args, **field_args))
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

def render_form(form, cols=2, exclude=[], state=None):
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

    items = get_tables(items, cols)
    if pages:
        pages = TAG('tabset', *[TAG('tab', get_tables(page['items']), heading=page['title']) for page in pages])
    else:
        pages = ''
    if state == 'write':
        attrs = {'ng-init': 'form.write=true'}
    else:
        attrs = {}
    attrs['class'] = 'form-view'
    items = DIV(items, pages, **attrs)
    return items
