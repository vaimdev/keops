
import json
from django.db import models
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_text

def _get_model(context):
    return ContentType.objects.get_by_natural_key(*context['model'].split('.')).model_class()

def field_text(value):
    if value is None:
        return ''
    elif isinstance(value, models.Model):
        return [{'id': value.pk, 'text': str(value)}]
    elif hasattr(value, '__call__'):
        return value()
    else:
        return str(value)

def search_text(queryset, text, search_fields=None):
    # Search by the search_fields property (Admin)
    if not search_fields:
        search_fields = queryset.model._admin.search_fields
    print(search_fields)
    if hasattr(queryset.model, '_admin'):
        filter = {f: text for f in search_fields}
    else:
        filter = {}
    return queryset.filter(**filter)

def grid(request):
    model_name = request.GET['model']
    model = ContentType.objects.get_by_natural_key(*model_name.split('.')).model_class()
    start = int(request.GET.get('start', '0'))
    limit = int(request.GET.get('limit', '25')) + start # settings
    queryset = model.objects.all()[start:limit]

    # Check content type permissions permissions

    get_val = lambda x: '' if x is None else x
    fields = ['pk'] + [f.name for f in model._meta.fields if not f.primary_key]
    rows = [{ f: smart_text(get_val(getattr(row, f))) for f in fields } for row in queryset]
    data = {'items': rows, 'total': model.objects.all().count()}
    return HttpResponse(json.dumps(data), content_type='application/json')

def _read(context):
    pk = context.get('pk')
    model = _get_model(context)
    start = int(context.get('start', '0'))
    limit = int(context.get('limit', '1')) + start # settings
    if pk:
        queryset = model.objects.filter(pk=pk)
        count = 1
    else:
        if 'id' in context:
            queryset = model.objects.filter(pk=context['id'])
        else:
            queryset = model.objects.all()[start:limit]
        count = model.objects.all().count()
        
    # TODO Check model permission
    
    fields = ['pk', '__str__'] + [f.name for f in model._meta.fields if not f.primary_key]
    rows = [{ f: field_text(getattr(row, f)) for f in fields } for row in queryset]
    return {'items': rows, 'total': count}
    
def read(request):
    return HttpResponse(json.dumps(_read(request.GET)), content_type='application/json')

def lookup(request):
    context = request.GET
    model = _get_model(context)
    start = int(context.get('start', '0'))
    limit = int(context.get('limit', '25')) + start # settings
    query = context.get('query', '')
    if query == '':
        queryset = model.objects.all()
    else:
        queryset = search_text(model.objects.all(), query)
    data = {'items': [{'id': obj.pk, 'text': str(obj)} for obj in queryset[start:limit]], 'total': queryset.count()}
    return HttpResponse(json.dumps(data), content_type='application/json')

def _submit(request, model, data):
    """
    Submit nested data (ManyToMany/OneToMany).
    """
    pass

def submit(request):
    """
    Default data submit view.
    """
    pk = request.POST.get('pk')
    model = _get_model(request.POST)
    data = json.loads(request.POST['data'])
    result = {'success': True}
    if data:
        obj = model.objects.get(pk=pk) if pk else model()
        for k, v in data.items():
            setattr(obj, k, v)
            print(k, v)
        obj.save()
    result['data'] = _read({'model': request.POST['model'], 'pk': obj.pk})['items'][0]
    return HttpResponse(json.dumps(result), content_type='application/json')
