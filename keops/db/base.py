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

    _new = models.base.ModelBase.__new__

    def __new__(cls, name, bases, attrs):
        meta = attrs.get('Meta')

        # IMPORTANT
        # Force model proxy to allow add fields, this model inheritance
        # is very important for any modular ERP based structure
        proxy_fields = None
        if meta and getattr(meta, 'proxy', None):
            proxy_fields = [(f, attrs.pop(f)) for f in [attr for attr, v in attrs.items() if isinstance(v, models.Field)]]

        new_class = ModelBase._new(cls, name, bases, attrs)

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


# Change Model.save method to trigger events
class Model(object):

    _delete = models.Model.delete
    _save = models.Model.save
    _setattr = models.Model.__setattr__
    _init = models.Model.__init__
    _str = models.Model.__str__

    # Optimization for commit only modified fields
    def __init__(self, *args, **kwargs):
        self._modified_fields = []
        Model._init(self, *args, **kwargs)
        if self.pk:
            self._modified_fields = []

    def __str__(self):
        """
        Auto detect default_fields attribute.
        """
        admin = getattr(self.__class__._meta, 'Admin', None)
        if admin:
            d = getattr(admin, 'default_fields', None)
            if d is None:
                for f in self.__class__._meta.fields:
                    if isinstance(f, models.CharField):
                        d = [f.name]
                        break
                setattr(admin, 'default_fields', d)
            if d:
                s = "_ = lambda self: %s"
                l = {}
                if isinstance(d, (tuple, list)):
                    exec(s % ' + " - " + '.join(['str(self.%s)' % s for s in d]), globals(), l)
                m = l.get('_')
                if m:
                    setattr(self.__class__, '__str__', m)
            else:
                setattr(self.__class__, '__str__', Model._str)
        return self.__class__.__str__(self)

    def __copy__(self):
        self.id = self.pk = None
        return self

    # Monkey patch
    #models.Model.__init__ = __init__
    #models.Model.delete = delete
    #models.Model.save = save
    #models.Model._save_table = _save_table
    #models.Model.__setattr__ = __setattr__
    models.Model.__str__ = __str__
    models.Model.__copy__ = __copy__
