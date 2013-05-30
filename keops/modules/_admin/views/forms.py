
from django.shortcuts import render
#from keops.modules.form.options import ModelAdmin
from keops.modules.admin.sites import site

def response_action(request, action):
    view_type = request.GET.get('view_type', action.view_type)
    if action.form:
        pass
    else:
        model = action.model.content_type.model_class()
        #admin_class = type("%sAdmin" % model.__name__, (ModelAdmin,), {})
        from django.forms import models
        form = models.modelform_factory(model)(request)
        return show(request, form, view_type)
        
def show(request, form, view_type):

    import json
    from django import forms
    from keops.forms import extjs
    
    f = form
    
    if view_type == 'list':
        template = 'form/list_form.js'
        fields = [name for name, field in form.get_form().base_fields.items() if not isinstance(field, forms.ModelMultipleChoiceField)]
        items = None
    else:
        #return form.add_view(request)
        template = 'form/model_form.js'
        fields = [name for name, field in f.base_fields.items()]
        items = json.dumps(extjs.get_form_items(f))
    fields = json.dumps(fields + ['pk'])
    
    
    
    return render(request, template, {'form': f, 'model': model,
        'json': json, 'fields': fields, 'extjs': extjs, 'items': items,
        'model_name': '%s.%s' % (model._meta.app_label, model._meta.model_name),
        'form_title': model._meta.verbose_name_plural})
