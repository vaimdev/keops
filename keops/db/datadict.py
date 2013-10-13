# This module implements ADD (Active Data Dictionary) on Django default classes
# Sorry! Monkey patch is the only way to do this for now
import copy
from django.db import models, connections, router, transaction, DatabaseError
from django import forms
from django.utils.translation import ugettext_lazy as _
from keops.forms.admin import ModelAdmin

# Add data dict object to Django model (class Extra)
dd_items = {
    # Extra attributes
    'default_fields': None,
    'status_field': None, # main model status field representation
    'field_groups': {
        'display_fields': None,
        'editable_fields': None,
        'printable_fields': None,
        'list_fields': None,
        'searchable_fields': None,
        'filter_fields': None,
    },

    # Events
    'after_insert': None,
    'after_update': None,
    'after_delete': None,
    'after_save': None,
    'after_change': None,
    'before_insert': None,
    'before_update': None,
    'before_delete': None,
    'before_save': None,
    'before_change': None,
}

models.base.ModelState._modified_fields = []

class ModelBase(object):

    _new = models.base.ModelBase.__new__

    def __new__(cls, name, bases, attrs):
        admin = attrs.pop('Admin', None)
        meta = attrs.get('Meta')

        # IMPORTANT
        # Force model proxy to allow add fields, this model inheritance
        # is very important for any modular ERP based structure
        proxy_fields = None
        if meta and getattr(meta, 'proxy', None):
            proxy_fields = [(f, attrs.pop(f)) for f in [attr for attr, v in attrs.items() if isinstance(v, models.Field)]]

        new_class = ModelBase._new(cls, name, bases, attrs)

        if not admin:
            admin = getattr(new_class, 'Admin', None)

        # Add proxy fields
        if proxy_fields:
            for f in proxy_fields:
                new_class.add_to_class(f[0], f[1])

        # Add Extra class
        extra = getattr(new_class, 'Extra', None)
        if extra:
            base = extra
        else:
            base = object

        if not 'Extra' in attrs:
            extra = type('Extra', (base,), {})
            new_class.add_to_class('Extra', extra)

        for d, v in dd_items.items():
            if not hasattr(extra, d):
                setattr(extra, d, copy.copy(v))

        # Add Admin meta class to _admin model attribute
        new_class.add_to_class('_admin', ModelAdmin(admin))

        new_class._meta._log_fields = [f.name for f in new_class._meta.fields if not f.primary_key] +\
            [f.attname for f in new_class._meta.fields\
             if isinstance(f, models.ForeignKey) and not f.primary_key]

        # Auto detect display_expression
        if extra.default_fields is None:
            fk = None
            for f in new_class._meta.fields:
                if isinstance(f, models.CharField):
                    extra.default_fields = (f.name,)
                    break
                if isinstance(f, models.ForeignKey) and not fk:
                    fk = (f.name,)
            extra.default_fields = extra.default_fields or fk

        if not extra.field_groups.get('list_fields'):
            extra.field_groups['list_fields'] = [
                f.name for f in new_class._meta.fields \
                if not isinstance(f, (models.AutoField, models.ManyToManyField)) and\
                getattr(f, 'custom_attrs', {}).get('visible', not f.primary_key)]

        if not extra.field_groups.get('search_fields'):
            extra.field_groups['search_fields'] = extra.default_fields

        # Auto detect status_field
        if extra.status_field is None:
            try:
                f = new_class._meta.get_field('status')
                if f.choices:
                    extra.state_field = 'status'
            except:
                pass

        return new_class

    # Monkey-Patch - Adjust for multi datbase delete method support
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
        objs = [k for k, v in objs if router.allow_syncdb(using, k.model)]
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

    def delete(self, using=None):
        if not hasattr(self.__class__, 'Extra'):
            return Model._delete(self, using=using)
        extra = self.__class__.Extra

        # Before events
        if extra.before_delete:
            extra.before_delete(self, using=using)
        if extra.before_change:
            extra.before_change(self, using=using)

        r = Model._delete(self, using=using)

        # After events
        if extra.after_delete:
            extra.after_delete(self, using=using)
        if extra.after_change:
            extra.after_change(self, using=using)

        self._modified_fields = []
        return r

    delete.alters_data = True

    # Monkey-patch performance (update only modified fields)
    def save(self, *args, **kwargs):
        if hasattr(self, '_modified_fields') and not kwargs.get('force_insert') and not kwargs.get('force_update'):
            kwargs.setdefault('update_fields', self._modified_fields)
        if not hasattr(self.__class__, 'Extra'):
            return Model._save(self, *args, **kwargs)
        extra = self.__class__.Extra

        # Before events
        if extra.before_save:
            extra.before_save(self, *args, **kwargs)

        pk = self.pk
        if pk:
            if extra.before_update:
                extra.before_update(self, *args, **kwargs)
        else:
            if extra.before_insert:
                extra.before_insert(self, *args, **kwargs)

        if extra.before_change:
            extra.before_change(self, *args, **kwargs)

        r = Model._save(self, *args, **kwargs)

        # After events
        if extra.after_save:
            extra.after_save(self, *args, **kwargs)

        if pk:
            if extra.after_update:
                extra.after_update(self, *args, **kwargs)
        else:
            if extra.after_insert:
                extra.after_insert(self, *args, **kwargs)

        if extra.after_change:
            extra.after_change(self, *args, **kwargs)

        self._modified_fields = []
        return r

    save.alters_data = True

    # Monkey-Patch for performance optimization
    def _save_table(self, raw=False, cls=None, force_insert=False,
                    force_update=False, using=None, update_fields=None):
        """
        Does the heavy-lifting involved in saving. Updates or inserts the data
        for a single table.
        """
        meta = cls._meta
        non_pks = [f for f in meta.local_concrete_fields if not f.primary_key]

        if update_fields:
            non_pks = [f for f in non_pks
                       if f.name in update_fields or f.attname in update_fields]

        pk_val = self._get_pk_val(meta)
        pk_set = pk_val is not None
        if not pk_set and force_update:
            raise ValueError("Cannot force an update in save() with no primary key.")
        updated = False
        # If possible, try an UPDATE. If that doesn't update anything, do an INSERT.
        if pk_set and not force_insert:
            base_qs = cls._base_manager.using(using)
            values = [(f, None, (getattr(self, f.attname) if raw else f.pre_save(self, False)))
                      for f in non_pks]
            updated = self._do_update(base_qs, using, pk_val, values, update_fields)
            if force_update and not updated:
                raise DatabaseError("Forced update did not affect any rows.")
            #if update_fields and not updated:
            #    raise DatabaseError("Save with update_fields did not affect any rows.")
        if not updated:
            if meta.order_with_respect_to:
                # If this is a model with an order_with_respect_to
                # autopopulate the _order field
                field = meta.order_with_respect_to
                order_value = cls._base_manager.using(using).filter(
                    **{field.name: getattr(self, field.attname)}).count()
                self._order = order_value

            fields = meta.local_concrete_fields
            if not pk_set:
                fields = [f for f in fields if not isinstance(f, models.AutoField) and ((update_fields and f.attname in update_fields) or not update_fields)]

            update_pk = bool(meta.has_auto_field and not pk_set)
            result = self._do_insert(cls._base_manager, using, fields, update_pk, raw)
            if update_pk:
                setattr(self, meta.pk.attname, result)
        return updated

    # Log modified fields to simplify performance optimization
    def __setattr__(self, key, value):
        if hasattr(self, 'pk') and hasattr(self, '_modified_fields') and\
                not key in self._modified_fields and\
                (self.pk or (self.pk is None and not value is None)) and\
                hasattr(self._meta, '_log_fields') and\
                key in self._meta._log_fields:
            self._modified_fields.append(key)
        Model._setattr(self, key, value)

    def __str__(self):
        extra = self.__class__.Extra
        if getattr(extra, 'default_fields', None):
            s = "class _C():\n    def __str__(self):\n        return %s"
            l = {}
            if isinstance(extra.default_fields, str):
                exec(s % extra.default_fields, globals(), l)
            elif isinstance(extra.default_fields, (tuple, list)):
                exec(s % ' + " - " + '.join(['str(self.%s)' % s for s in extra.default_fields]), globals(), l)
            m = l.get('_C')
            if m:
                setattr(self.__class__, '__str__', m.__str__)
        else:
            setattr(self.__class__, '__str__', Model._str)
        return self.__class__.__str__(self)

    # Monkey patch
    models.Model.__init__ = __init__
    models.Model.delete = delete
    #models.Model.save = save
    #models.Model._save_table = _save_table
    #models.Model.__setattr__ = __setattr__
    models.Model.__str__ = __str__
