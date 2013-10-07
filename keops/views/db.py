import decimal
import datetime
import json
from django.utils.translation import ugettext as _
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import formats
from keops.db import get_db, set_db
from keops.http import HttpJsonResponse

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

def get_model(context):
    # TODO Check model permission
    # TODO CACHE PERMISSION
    model = context['model']
    if isinstance(model, str):
        return ContentType.objects.get_by_natural_key(*model.split('.')).model_class()
    else:
        return model

def field_text(value):
    if value is None:
        return ''
    elif callable(value):
        return value()
    elif isinstance(value, (int, str, float, decimal.Decimal)):
        return formats.localize(value)
    elif isinstance(value, datetime.datetime):
        return formats.date_format(value, 'SHORT_DATETIME_FORMAT')
    elif isinstance(value, models.Model):
        return {'label': str(value), 'value': value.pk}
    else:
        return str(value)


def _get_filter_args(self, filter):
    if isinstance(filter, (tuple, list)):
        d = {}
        for i in filter:
            d[i[0] + '__exact'] = i[2]
    elif isinstance(filter, dict):
        return filter

def _get_query_args(cls, search_fields, value, filter=None):
    op = '__icontains'
    # TODO add unaccent

    def _get_filter_items(field, expr=None):
        if expr:
            rs = expr + '__' + field.name
        else:
            rs = field.name
        if isinstance(field, models.ForeignKey):
            if field.related.parent_model == cls:
                return []
            r = []
            model = field.related.parent_model
            d = model.Extra.field_groups['search_fields']
            if isinstance(d, (tuple, list)):
                for f in d:
                    r.extend(_get_filter_items(model._meta.get_field(f), rs))
                return r
            else:
                r.extend(_get_filter_items(model._meta.get_field(d), rs))
                return r
        else:
            return [rs]

    if filter:
        d = _get_filter_args(filter)
    else:
        d = {}
    filter_items = []
    if isinstance(search_fields, (tuple, list)):
        r = None
        for f in search_fields:
            field = cls._meta.get_field(f)
            filter_items.extend(_get_filter_items(field))

        for f in filter_items:
            q = Q(**{f + op: value})
            if r:
                r = r | q
            else:
                r = q
        if d:
            r = Q(**d) & Q(r)
        return r

    else:
        filter_items.extend(_get_filter_items(cls._meta.get_field(cls._meta.default_fields)))
        d.update({f + op: value for f in filter_items})
        return Q(**d)

def search_text(queryset, text, search_fields=None):
    # Search by the search_fields property (Admin)
    # TODO add query on form view
    model = queryset.model
    if not search_fields:
        search_fields = model.Extra.field_groups['search_fields']

    query = _get_query_args(model, search_fields, text)

    return queryset.filter(query)

def grid(request):
    using = get_db(request)
    model = get_model(request.GET)
    pk = request.GET.get('pk')
    query = request.GET.get('query')
    field = request.GET.get('field') # Check related field
    if field:
        obj = model.objects.using(using).get(pk=pk)
        queryset = getattr(obj, field)
        field = getattr(model, field)
        model = field.related.model
        fields = field.list_fields
    else:
        queryset = model.objects.using(using)
        if hasattr(model, 'Extra'):
            fields = model.Extra.field_groups.get('list_fields')
        else:
            fields = None
        if isinstance(fields, tuple):
            fields = list(fields)
    fields = fields or [f.name for f in model._meta.concrete_fields if not f.primary_key]
    start = int(request.GET.get('start', '0'))
    limit = int(request.GET.get('limit', '50')) + start # settings
    count = request.GET.get('total', False)

    if query:
        queryset = search_text(queryset, query)

    if count:
        count = queryset.all().count()
    else:
        count = None

    queryset = queryset.all()[start:limit]

    # TODO Check content type permissions permissions

    get_val = lambda x: '' if x is None else x
    fields = ['pk'] + fields
    rows = [{f: str(get_val(getattr(row, f))) for f in fields} for row in queryset]
    data = {'items': rows, 'total': count}
    return HttpJsonResponse(data)

def get_read_fields(model):
    if not hasattr(model.Extra, '_cache_read_fields'):
        model.Extra._cache_read_fields = [f.name for f in model._meta.fields if not f.primary_key] +\
                                         [(f.choices and 'get_%s_display' % f.name) for f in model._meta.fields if f.choices]
    return model.Extra._cache_read_fields

def _read(context, using):
    pk = context.get('pk')
    queryset = context.get('queryset')
    if queryset:
        # TODO Check queryset model permission
        model = queryset.model
    else:
        model = get_model(context)
        queryset = model.objects
    count = queryset
    start = int(context.get('start', '0'))
    limit = int(context.get('limit', '1')) + start # settings
    if pk:
        queryset = queryset.using(using).filter(pk=pk)
    else:
        queryset = queryset.using(using).all()
        if not 'all' in context:
            queryset = queryset[start:limit]
    if 'total' in context:
        count = count.using(using).all().count()
    else:
        count = None

    fields = ['pk', '__str__'] + context.get('fields', get_read_fields(model))
    rows = [{f: field_text(getattr(row, f)) for f in fields} for row in queryset]
    return {'items': rows, 'total': count}
    
def read(request):
    using = get_db(request)
    # Prevent user get all records
    assert not 'all' in request.GET
    return HttpJsonResponse(_read(request.GET, using))

def _get_queryset_fields(model, obj, attr):
    # TODO get fields for relation attr
    return getattr(obj, attr)

def read_items(request):
    using = get_db(request)
    # Force get all items
    context = {'all': None}
    model = get_model(request.GET)
    items = json.loads(request.GET['items'])
    pk = request.GET['pk']
    data = {}
    # Optimize selecting pk field only
    obj = model.objects.using(using).only(model._meta.pk.name).get(pk=pk)
    for item in items:
        context['fields'] = [] # Select only pk, __str__ for now
        context['queryset'] = _get_queryset_fields(model, obj, item)
        data[item] = _read(context, using)
    return HttpJsonResponse(data)

def lookup(request):
    context = request.GET
    model = get_model(context)
    start = int(context.get('start', '0'))
    limit = int(context.get('limit', '25')) + start # settings
    query = context.get('query', '')
    if query == '':
        queryset = model.objects.all()
    else:
        queryset = model.objects.all()
        #queryset = search_text(model.objects.all(), query)
    data = [{'value': obj.pk, 'label': str(obj)} for obj in queryset[start:limit]]
    return HttpJsonResponse(data)

def _save(context, using):
    """
    Save context data on using specified database.
    """
    pk = context.get('pk')
    model = get_model(context)
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
        _save_item(json.loads(related), obj, using)
    return True, obj

def _save_item(data, parent, using):
    """
    Save item data rows (ManyToMany/OneToMany).
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
    model = get_model(context)
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
    return HttpJsonResponse(result)
