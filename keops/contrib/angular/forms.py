from django.utils.translation import ugettext_lazy as _
from django.forms.util import flatatt
from django.utils import formats
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms import widgets
import django.forms

class Select(widgets.Select):
    def render(self, name, value, attrs=None, choices=()):
        if not attrs:
            attrs = {}
        if value and 'ng-model' in attrs:
            attrs['ng-init'] = "%s = '%s'" % (attrs['ng-model'], value)
        return super(Select, self).render(name, value, attrs, choices)

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(Select, self).build_attrs(extra_attrs, **kwargs)
        attrs.setdefault('ng-model', kwargs.get('name'))
        attrs['combobox'] = 'combobox'
        return attrs

class DateInput(widgets.DateInput):
    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        if value:
            attrs['ng-init'] = "%s = '%s'" % (name, value)
        show = attrs.pop('ng-show', '')
        return '<div class="input-append" style="display: inline;" ng-show="%s">%s</div>' % (show, super(DateInput, self).render(name, value, attrs))

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(DateInput, self).build_attrs(extra_attrs, **kwargs)
        attrs.setdefault('ng-model', kwargs.get('name'))
        attrs['date-picker'] = 'date-picker'
        attrs['date-format'] = _('yy-mm-dd')
        attrs['ui-mask'] = _('9999-99-99')
        attrs['type'] = 'text'
        attrs.setdefault('class', 'form-date-field')
        return attrs

class DateTimeInput(DateInput):
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(DateTimeInput, self).build_attrs(extra_attrs, **kwargs)
        del attrs['date-picker']
        attrs['date-time-picker'] = 'date-time-picker'
        attrs['time-format'] = _('HH:mm')
        attrs['ui-mask'] = _('9999-99-99 99:99 AA')
        return attrs

django.forms.ChoiceField.widget = Select
django.forms.DateField.widget = DateInput
django.forms.DateTimeField.widget = DateTimeInput
