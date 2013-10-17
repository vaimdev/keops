from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms import widgets
import django.forms

class Select(widgets.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        final_attrs['ng-init'] = "%s = '%s'" % (name, value)
        output = [format_html('<select{0}>', flatatt(final_attrs))]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(Select, self).build_attrs(extra_attrs, **kwargs)
        attrs['ng-model'] = kwargs.get('name')
        attrs['combobox'] = 'combobox'
        return attrs

django.forms.ChoiceField.widget = Select
