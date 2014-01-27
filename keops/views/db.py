import datetime
import json
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from keops.db import models
from keops.db import get_db
from keops.http import HttpJsonResponse
from keops.utils import field_text
from keops.utils.filter import search_text
from keops.admin import site


def get_model(context):
    return site.get_model(context['model'])


def _choice_fields(model):
    if not hasattr(model._meta.admin, '_cache_choice_fields'):
        model._meta.admin._cache_choice_fields = {f.name: 'get_%s_display' % f.name for f in model._meta.fields if f.choices}
    return model._meta.admin._cache_choice_fields


def fk_select_fields(model):
    if not hasattr(model._meta.admin, '_cache_fk_select_fields'):
        model._meta.admin._cache_fk_select_fields = {f.name: f.custom_attrs['select_fields'] for f in model._meta.fields if 'select_fields' in f.custom_attrs}
    return model._meta.admin._cache_fk_select_fields


def _display_fn(model):
    if not hasattr(model._meta.admin, '_cache_display_fn'):
        r = {}
        for field in model._meta.all_fields:
            if field.custom_attrs.display_fn:
                display = field.custom_attrs.display_fn
            elif isinstance(field, models.ForeignKey) and field.custom_attrs.default_fields:
                fields = field.custom_attrs.default_fields
                display = lambda x: ' - '.join([str(getattr(x, f, '') or '') for f in fields])
            else:
                display = str
            r[field.name] = display
        model._meta.admin._cache_display_fn = r
    return model._meta.admin._cache_display_fn


def grid(request):
    # TODO use grid method for specific model admin
    using = get_db(request)
    model = get_model(request.GET)
    pk = request.GET.get('pk')
    query = request.GET.get('query')
    field = request.GET.get('field')  # Check related field
    disp_fields = {}
    if field:
        obj = model.objects.using(using).get(pk=pk)
        queryset = getattr(obj, field)
        field = getattr(model, field)
        model = field.related.model
        fields = field.list_fields
    else:
        queryset = model.objects.using(using)
        fields = model._meta.admin.field_groups.get('list_fields')
        disp_fields = _choice_fields(model)
        if isinstance(fields, tuple):
            fields = list(fields)
    fields = fields or [f.name for f in model._meta.concrete_fields if not f.primary_key]
    start = int(request.GET.get('start', '0'))
    limit = int(request.GET.get('limit', '50')) + start  # settings
    count = request.GET.get('total', False)

    if query:
        queryset = search_text(queryset, query)

    if count:
        count = queryset.all().count()
    else:
        count = None

    queryset = queryset.all()[start:limit]

    # TODO Check content type permissions permissions

    get_val = lambda x: isinstance(x, datetime.date) and field_text(x) or ('' if x is None else (callable(x) and x()) or x)
    fields = ['pk'] + fields
    display_fn = _display_fn(model)
    rows = [{f: display_fn.get(f, str)(get_val(getattr(row, disp_fields.get(f, f)))) for f in fields} for row in queryset]
    data = {'items': rows, 'total': count}
    return HttpJsonResponse(data)


def _read_fields(model):
    if not hasattr(model._meta.admin, '_cache_read_fields'):
        model._meta.admin._cache_read_fields = [f.name for f in model._meta.fields if not f.primary_key] +\
            [f.name for f in model._meta.virtual_fields if isinstance(f, models.PropertyField)]
    return model._meta.admin._cache_read_fields


def prepare_read(context, using):
    pk = context.get('pk')
    queryset = context.get('queryset')
    if queryset:
        # TODO Check queryset model permission
        model = queryset.model
    else:
        model = get_model(context)
        queryset = model._default_manager
    count = queryset
    start = int(context.get('start', '0'))
    limit = int(context.get('limit', '1')) + start
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
    fields = ['pk', '__str__'] + context.get('fields', _read_fields(model))
    disp_fields = _choice_fields(model)
    display_fn = _display_fn(model)
    rows = [{f: field_text(getattr(row, f), row, f, disp_fields.get(f, f), display_fn=display_fn.get(f, str)) for f in fields} for row in queryset]
    return {'items': rows, 'total': count}


def read(request):
    # Prevent get all records
    assert not 'all' in request.GET
    model = get_model(request.GET)
    return model._meta.admin.model_admin.read(request)


def _get_queryset_fields(model, obj, attr):
    # TODO get select fields for relation attr
    return getattr(obj, attr)


def read_items(request):
    from django.db.models.fields.related import ReverseManyRelatedObjectsDescriptor
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
        field = getattr(model, item)
        if getattr(field, 'list_display', None):
            context['fields'] = field.list_display
        if isinstance(field, ReverseManyRelatedObjectsDescriptor):
            data[item] = [{'id': r.id, 'text': str(r)} for r in getattr(obj, item).all()]
        else:
            context['queryset'] = _get_queryset_fields(model, obj, item)
            data[item] = prepare_read(context, using)
    return HttpJsonResponse(data)


def lookup(request):
    model = get_model(request.GET)
    return model._meta.admin.model_admin.lookup(request, sel_fields=fk_select_fields(model), display_fn=_display_fn(model)[request.GET['field']])


def new_item(request):
    return get_model(request.GET)._admin.new_item(request)


def field_change(request):
    return get_model(request.GET)._admin.field_change(request)


def submit(request):
    """
    Default data submit view.
    """
    data = json.loads(request.body.decode(settings.DEFAULT_CHARSET))
    request.POST = data
    model = get_model(data)
    return model._admin.submit(request)
