# This module implements ADD (Active Data Dictionary) on Django default classes

from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from keops.forms.admin import ModelAdmin

# Add data dict object to Django model (class Extra)
dd_items = {
    # Extra attributes
    'display_expression': None,
    'state_field': None, # main state field representation
    'field_groups': {
        'edit_fields': [],
        'print_fields': [],
        'search_fields': [],
        'filter_fields': [],
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

class ModelBase(object):

    _new = models.base.ModelBase.__new__

    def __new__(cls, name, bases, attrs):
        admin = attrs.pop('Admin', None)
        meta = attrs.get('Meta', None)

        # IMPORTANT!
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

        # Add Admin meta class to _admin model attribute
        new_class.add_to_class('_admin', ModelAdmin(admin))

        extra = getattr(new_class, 'Extra', None)
        if extra:
            for d, v in dd_items.items():
                if not hasattr(extra, d):
                    setattr(extra, d, v)
        else:
            extra = type('Extra', (object,), dd_items.copy())
            new_class.add_to_class('Extra', extra)

        # Auto detect display_expression
        if extra.display_expression is None:
            field = None
            for f in new_class._meta.concrete_fields:
                if isinstance(f, (models.CharField, models.ForeignKey)):
                    field = f.name
                    break
            extra.display_expression = field

        # Convert display_expression to __str__ method
        if extra.display_expression:
            m = models.Model.__str__
            if m is new_class.__str__:
                s = "def __str__(self):\n    return %s"
                l = {}
                if isinstance(extra.display_expression, str):
                    exec(s % extra.display_expression, globals(), l)
                elif isinstance(extra.display_expression, (tuple, list)):
                    exec(s % ' + " - " + '.join(['str(self.%s)' % s for s in extra.display_expression]), globals(), l)
                m = l.get('__str__', m)
            setattr(new_class, '__str__', m)

        # Auto detect state_field
        if extra.state_field is None:
            try:
                f = new_class._meta.get_field('state')
                if f.choices:
                    extra.state_field = 'state'
            except:
                pass

        return new_class

    models.base.ModelBase.__new__ = __new__

# Change Model.save method to trigger events
class Model(object):

    _delete = models.Model.delete
    _save = models.Model.save
    _setattr = models.Model.__setattr__
    _init = models.Model.__init__

    # Optimization for commit only modified fields
    def __init__(self, *args, **kwargs):
        self._modified_fields = []
        Model._init(self, *args, **kwargs)
        if self.pk:
            self._modified_fields = []

    def delete(self, *args, **kwargs):
        if not hasattr(self.__class__, 'Extra'):
            return Model._save(self, *args, **kwargs)
        extra = self.__class__.Extra
        # Before events
        if extra.before_delete:
            extra.before_delete(self, *args, **kwargs)
        if extra.before_change:
            extra.before_change(self, *args, **kwargs)

        r = Model._delete(self, *args, **kwargs)

        # After events
        if extra.after_delete:
            extra.after_delete(self, *args, **kwargs)
        if extra.after_change:
            extra.after_change(self, *args, **kwargs)

        self._modified_fields = []
        return r

    def save(self, *args, **kwargs):
        if hasattr(self, '_modified_fields') and not kwargs.get('force_insert', None):
            kwargs.setdefault('update_fields', self._modified_fields)
        print(self.__class__.__name__, kwargs)
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

    # Path for performance optimization
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
                raise models.DatabaseError("Forced update did not affect any rows.")
            if update_fields and not updated:
                raise models.DatabaseError("Save with update_fields did not affect any rows.")
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
        if hasattr(self, 'pk') and hasattr(self, '_modified_fields') and not key in self._modified_fields:
            if self.pk or (self.pk is None and not value is None):
                self._modified_fields.append(key)
        Model._setattr(self, key, value)

    models.Model.__init__ = __init__
    models.Model.delete = delete
    models.Model.save = save
    models.Model._save_table = _save_table
    models.Model.__setattr__ = __setattr__
