from django.utils import six
from django.forms import forms
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

class View(object):
    template_name = 'keops/forms/view.html'

    def get_form(self):
        return self
    
    def render(self, request, template, context):
        from django.shortcuts import render
        context['form'] = self
        return render(request, template, context)

    def view(self, request, **kwargs):
        """
        Render a form instance.
        """
        return self.render(request, self.template_name, kwargs)

    def submit(self, request, **kwargs):
        """
        Receive data.
        """
        pass

class BaseForm(forms.BaseForm, View):
    pass

class Form(six.with_metaclass(forms.DeclarativeFieldsMetaclass, BaseForm)):
    pass
