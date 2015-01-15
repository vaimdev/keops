from django.db import models
from django.db.models import Q


def _get_filter_args(filter):
    if isinstance(filter, (tuple, list)):
        d = {}
        for i in filter:
            d[i[0] + '__exact'] = i[2]
    elif isinstance(filter, dict):
        return filter


def _get_query_args(cls, search_fields, value, filter=None):
    op = '__icontains'

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
