import json
from django.utils.translation import ugettext as _
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_text
from keops.db import get_db, set_db

def index(request):
    """
    Set default db alias session value.
    """
    # set default _db_alias to 'alias'
    assert request.method == 'GET'
    alias = request.GET.get('alias')
    if alias:
        set_db(alias)
        next = request.GET.get('next')
        if next:
            return HttpResponseRedirect(next)
    return HttpResponse(get_db())

def _get_model(context):
    # Check permission
    # TODO CACHE PERMISSION
    model = context['model']
    if isinstance(model, str):
        return ContentType.objects.get_by_natural_key(*model.split('.')).model_class()
    else:
        return model

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
    if hasattr(queryset.model, '_admin'):
        filter = {f: text for f in search_fields}
    else:
        filter = {}
    return queryset.filter(**filter)

def grid(request):
    model_name = request.GET['model']
    model = ContentType.objects.get_by_natural_key(*model_name.split('.')).model_class()
    start = int(request.GET.get('start', '0'))
    limit = int(request.GET.get('limit', '50')) + start # settings
    queryset = model.objects.all()[start:limit]

    # Check content type permissions permissions

    get_val = lambda x: '' if x is None else x
    fields = ['pk'] + [f.name for f in model._meta.fields if not f.primary_key]
    rows = [{f: smart_text(get_val(getattr(row, f))) for f in fields} for row in queryset]
    data = {'items': rows, 'total': model.objects.all().count()}
    return HttpResponse(json.dumps(data), content_type='application/json')

def _read(context, using):
    pk = context.get('pk')
    model = _get_model(context)
    start = int(context.get('start', '0'))
    limit = int(context.get('limit', '1')) + start # settings
    if pk:
        queryset = model.objects.using(using).filter(pk=pk)
        count = 1
    else:
        if 'id' in context:
            queryset = model.objects.using(using).filter(pk=context['id'])
        else:
            queryset = model.objects.using(using).all()[start:limit]
        count = model.objects.using(using).all().count()
        
    # TODO Check model permission
    
    fields = ['pk', '__str__'] + [f.name for f in model._meta.fields if not f.primary_key]
    rows = [{f: field_text(getattr(row, f)) for f in fields} for row in queryset]
    return {'items': rows, 'total': count}
    
def read(request):
    using = get_db(request)
    return HttpResponse(json.dumps(_read(request.GET, using)), content_type='application/json')

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

def _save(context, using):
    """
    Save context data on using specified database.
    """
    pk = context.get('pk')
    model = _get_model(context)
    data = context.get('data')
    obj = None
    if pk:
        obj = model.objects.using(using).get(pk=pk)
    if data:
        if isinstance(data, str):
            data = json.loads(data)
        obj = obj or model()
        for k, v in data.items():
            setattr(obj, k, v)
        obj.save(using=using)

        # submit related data
    related = context.get('related')
    if related:
        _save_related(json.loads(related), obj, using)
    return True, obj

def _save_related(data, parent, using):
    """
    Save nested/related data rows (ManyToMany/OneToMany).
    """
    for obj in data:
        model = models.get_model(*obj['model'].split('.'))
        link_field = obj['linkField']
        rows = obj['data']
        for row in rows:
            action = row.get('action')
            record = row.get('data')
            pk = row.get('pk')
            if action == 'DELETE':
                model.objects.using(using).get(pk=pk).delete()
                continue
            elif action == 'CREATE':
                record[link_field] = parent.pk
            context = {'pk': pk, 'model': model, 'data': record}
            _save(context, using)

def _delete(context, using):
    """
    Default delete operation.
    """
    model = _get_model(context)
    obj = model.objects.using(using).get(pk=context['pk'])
    obj.delete(using=using)
    return {
        'success': True,
        'action': 'DELETE',
        'label': _('Success'),
        'msg': _('Record successfully deleted!'),
    }

def submit(request):
    """
    Default data submit view.
    """
    using = get_db(request)
    if request.method == 'DELETE':
        result = _delete(request.GET, using)
    else:
        success, obj = _save(request.POST, using)
        result = {'success': success, 'data': _read({'model': request.POST['model'], 'pk': obj.pk}, using)['items'][0]}
    return HttpResponse(json.dumps(result), content_type='application/json')
