from django.utils.translation import ugettext as _
from django.utils import formats
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django import forms
import keops.forms
from keops.utils.html import *
from keops.forms import widgets

def get_field(field):
    bound_field = field
    field = bound_field.field
    name = bound_field.name
    attrs = {'ng-show': 'form.write', 'ng-model': 'form.item.' + name}
    span = {'ng-bind': 'form.item.' + name}
    widget_args = []
    if field.required:
        attrs['required'] = 1
    if isinstance(field, forms.BooleanField):
        span['ng-bind'] = "form.item.%s ? '%s': (form.item.%s == false ? '%s': '')" % (name, capfirst(_('yes')), name, capfirst(_('no')))
    elif isinstance(field, forms.ModelMultipleChoiceField):
        attrs['tag'] = 'div multiplechoice remoteitem'
        attrs['style'] = 'padding-top: 16px;';
        attrs['name'] = name
        attrs['label'] = bound_field.label
        span['ng-bind'] = 'item.__str__'
    elif isinstance(field, forms.ModelChoiceField):
        # Change to smart combobox widget
        meta = field.queryset.model._meta
        attrs['name'] = field.target_attr.attname
        attrs['ng-model'] = 'form.item.' + field.target_attr.attname
        attrs['model-name'] = '%s.%s' % (meta.app_label, meta.model_name)
        span['tag'] = 'a'
        span['ng-click'] = "openResource('%s', 'pk='%s)" % (field.target_attr.get_resource_url(), ' + form.item.%s' % field.target_attr.attname)
        span['style'] = 'cursor: pointer;'

    if not isinstance(field, forms.BooleanField):
        attrs['class'] = 'long-field'

    if isinstance(field, forms.ModelMultipleChoiceField):
        field_args = {'colspan': 2}
        args = [bound_field.label_tag(attrs={'class': 'field-label', 'ng-show': '!form.write'}, label_suffix=' ')]
        label = None
        bind = span.pop('ng-bind')
        span['ng-repeat'] = 'item in form.item.' + name
        span_args = [TAG('li', '<i class="icon-li icon-ok"></i><a ng-bind="%s"></a>' % bind, **span)]
        span = {'class': 'icons-ul'}
        span_tag = 'ul'
    elif isinstance(field, keops.forms.GridField):
        field_args = {'colspan': 2, 'style': 'width: 100%;'}

        attrs['tag'] = 'table remoteitem'
        #attrs['style'] = 'padding-top: 16px;';
        attrs['name'] = name
        attrs.pop('ng-show')
        span['ng-bind'] = 'item.__str__'
        print(field.target_attr.list_fields)
        widget_args = [TABLE(THEAD(TR(TH(''), TH('__str__'))),
                             TBODY(TR(
                                 '<td style="width: 1px; padding-right: 10px;"><i style="cursor: pointer" title="' + _('Remove item') + '" class="icon-remove"></a></td>',
                                 TD('{{item.__str__}}'),
                                      attrs={'ng-repeat': 'item in form.item.' + name})),
                             attrs={'style': 'table-layout: inherit;'})]

        args = [bound_field.label_tag(attrs={'class': 'field-label', 'style': 'display: inline-block; padding-right: 10px;'}, label_suffix=' '), TAG('a', 'Add', attrs={'class': 'btn'})]
        label = None
        span = {}
        span_args = []
        span_tag = None

    else:
        label = bound_field.label_tag(attrs={'class': 'field-label'}, label_suffix=' ')
        field_args = {'class': 'field-cell'}
        args = []
        span_args = []
        span_tag = 'span'

    if 'tag' in attrs:
        widget = TAG(attrs.pop('tag'), id=bound_field.auto_id, name=attrs.pop('name', None) or name, *widget_args, **attrs)
    else:
        widget = bound_field.as_widget(attrs=attrs)

    r = []
    if label:
        r = [TD(label, attrs={'class': 'label-cell'})]
    args.append(widget)
    if span_tag:
        args.append(TAG(span_tag, attrs={'ng-show': '!form.write'}, *span_args, **span))
    r.append(TD(*args, **field_args))
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

    return TABLE(TR(*[TD(t, style='width: 50%') for t in tables]))

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
