# This module implements ADD (Active Data Dictionary) on Django default classes
import copy
from django.db import models, router, DatabaseError
from django.db.models import options
from django.apps import apps

options.DEFAULT_NAMES += ('Admin',)
models.base.ModelState._modified_fields = []


def get_model(model):
    return apps.get_model(*model.split('.'))


class ModelBase(object):
    def __new__(cls, name, bases, attrs):
        meta = attrs.get('Meta')

        # IMPORTANT
        # Force model proxy to allow add fields, this model inheritance
        # is very important for any modular ERP based structure
        proxy_fields = None
        if meta and getattr(meta, 'proxy', None):
            proxy_fields = [(f, attrs.pop(f)) for f in [attr for attr, v in attrs.items() if isinstance(v, models.Field)]]

        new_class = models.base.ModelBase.__new__(cls, name, bases, attrs)

        # Add proxy fields
        if proxy_fields:
            for f in proxy_fields:
                new_class.add_to_class(f[0], f[1])

        new_class._meta._log_fields = [f.name for f in new_class._meta.fields if not f.primary_key] +\
            [f.attname for f in new_class._meta.fields\
             if isinstance(f, models.ForeignKey) and not f.primary_key]

        return new_class

    # Monkey-Patch - Adjust for multi database delete method support
    # detect only db installed apps models
    def get_all_related_objects(self, local_only=False, include_hidden=False,
                                include_proxy_eq=False):
        using = router.db_for_write(self.model)
        objs = models.base.Options.get_all_related_objects_with_model(
                self,
                local_only=local_only,
                include_hidden=include_hidden,
                include_proxy_eq=include_proxy_eq
        )
        objs = [k for k, v in objs if router.allow_migrate(using, k.model)]
        return objs

    # Monkey patch
    models.base.Options.get_all_related_objects = get_all_related_objects
    models.base.ModelBase.__new__ = __new__


class Model(object):
    # Optimization: commit only modified fields
    def __init__(self, *args, **kwargs):
        self.__modified_fields = []
        models.Model.__init__(self, *args, **kwargs)
        if self.pk:
            self.__modified_fields = []

    def __copy__(self):
        self.id = self.pk = None
        return self

    # Monkey patch
    models.Model.__init__ = __init__
    models.Model.__copy__ = __copy__
