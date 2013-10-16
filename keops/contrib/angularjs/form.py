from django.utils.translation import ugettext as _
from django.utils import formats
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django import forms
import django.forms.widgets
import keops.forms
from keops.utils.html import *
from keops.forms import widgets

def get_field(field, form=None):
    bound_field = field
    field = bound_field.field
    name = bound_field.name
    attrs = {'ng-show': 'form.write', 'ng-model': 'form.item.' + name}
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

    if isinstance(field, forms.ChoiceField):
        attrs['combobox'] = ''

    if isinstance(field, forms.BooleanField):
        attrs = {'tag': 'label', 'ng-show': attrs.pop('ng-show'), 'style': 'cursor: pointer;'}
        widget_args = [TAG('input type="checkbox"', ngModel='form.item.' + name)]
        #span['ng-bind'] = "form.item.%s" % name
        span['ng-bind'] = "form.item.%s ? '%s': '%s'" % (name, capfirst(_('yes')), capfirst(_('no')))
    elif isinstance(field, forms.DateTimeField):
        attrs['ui-mask'] = _('9999-99-99 99:99 AA')
        attrs['date-format'] = _('yy-mm-dd')
        attrs['time-format'] = _('HH:mm')
        span_args.append('{{%s | dateFromNow}}' % span.pop('ng-bind'))
        show = attrs.pop('ng-show')
        widget_args.append(TAG('input type="text" date-time-picker', **attrs))
        attrs = {'tag': 'div', 'ng-show': show, 'class': 'input-append date'}
    elif isinstance(field, forms.DateField):
        attrs['ui-mask'] = _('9999-99-99')
        attrs['date-format'] = _('yy-mm-dd')
        span_args.append('{{%s | dateFrom}}' % span.pop('ng-bind'))
        show = attrs.pop('ng-show')
        widget_args.append(TAG('input type="text" date-picker', **attrs))
        attrs = {'tag': 'div', 'ng-show': show, 'class': 'input-append date'}
    elif isinstance(field, forms.EmailField):
        span_tag = 'a'
        span['ng-href'] = 'mailto:{{form.item.%s}}' % name
    elif field.target_attr.choices:
        span['ng-bind'] = 'form.item.get_%s_display' % name
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
        widget_args = [
            TABLE(
                THEAD(
                    TR(
                        TH(''),
                        TH(''), # remove link column
                    )
                ),
                TBODY(
                    TR(
                        TD('{{item.__str__}}'),
                        TD(
                            '<i ng-show="form.write" style="cursor: pointer" title="%s" class="icon-remove"></i>''' % capfirst(_('remove item')),
                            style='width: 1px;'
                        ),
                        attrs={'ng-repeat': 'item in form.item.' + name}
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
                attrs={'ng-show': 'form.write', 'class': 'btn'}
            )
        ]
        label = None
        span = {}
        span_args = []
        span_tag = None

    elif isinstance(field, forms.ModelChoiceField):
        widget_args.append(
            TAG('input combobox type="hidden" ng-model="%s"' % attrs.pop('ng-model'),
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
        attrs['style'] = 'height: 70px; margin: 0;'
    elif isinstance(field, forms.DecimalField):
        attrs['tag'] = 'input ui-money'
        attrs['ui-money-thousands'] = formats.get_format('THOUSAND_SEPARATOR')
        attrs['ui-money-decimal'] = formats.get_format('DECIMAL_SEPARATOR')
        attrs['ui-money-negative'] = True
        span_args.append('{{%s | number:2}}' % span.pop('ng-bind'))

    if readonly:
        attrs['ng-init'] = 'form.readonly.%s = true' % name
        if 'ng-show' in attrs:
            attrs['ng-show'] += ' && !form.readonly.%s' % name

    if 'tag' in attrs:
        widget = TAG(attrs.pop('tag'), id=bound_field.auto_id, name=attrs.pop('name', None) or name, *widget_args, **attrs)
    else:
        widget = bound_field.as_widget(attrs=attrs)

    r = []
    if label:
        r = [TD(label, attrs={'class': 'label-cell'})]
    args.append(widget)
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
                    fields.append(''.join(get_field(container[0], form)))
                else:
                    fields.append(get_container(container))

    items = get_tables(items, cols)
    if pages:
        pages = TAG('tabset', *[TAG('tab', get_tables(page['items']), heading=page['title']) for page in pages])
    else:
        pages = ''
    items = DIV(items, pages, attrs={'class': 'form-view'})
    return items
