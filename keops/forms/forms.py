
from django.utils import six
from django.forms import forms

class AbstractForm(object):
    template = 'keops/forms/form.js'
    
    def render(self, request, template, context):
        from django.shortcuts import render
        context['form'] = self
        return render(request, template, context)
    
    def view(self, request, **kwargs):
        """Render a form instance."""
        return self.render(request, self.template, kwargs)

class BaseForm(forms.BaseForm, AbstractForm):
    pass

class Form(six.with_metaclass(forms.DeclarativeFieldsMetaclass, BaseForm)):
    pass
