# This module implements ADD (Active Data Dictionary) on Django default classes

from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from keops.forms.admin import ModelAdmin

# Add data dict object to Django model (class Extra)
dd_items = {
    # Extra attributes
    'display_expression': None,
    'field_groups': {
        'editable_fields': [],
        'printable_fields': [],
        'search_fields': [],
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
        new_class = ModelBase._new(cls, name, bases, attrs)
        if not admin:
            admin = getattr(new_class, 'Admin', None)
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

        return new_class

    models.base.ModelBase.__new__ = __new__

# Change Model.save method to trigger events
class Model(object):

    _delete = models.Model.delete
    _save = models.Model.save
    _setattr = models.Model.__setattr__
    _init = models.Model.__init__

    # Optimize for commit only modified fields
    def __init__(self, *args, **kwargs):
        self.__modifiedfields__ = []
        Model._init(self, *args, **kwargs)
        if self.pk:
            self.__modifiedfields__ = []

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

        self.__modifiedfields__ = []
        return r

    def save(self, *args, **kwargs):
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

        self.__modifiedfields__ = []
        return r

    # Log modified fields
    def __setattr__(self, key, value):
        if hasattr(self, 'pk') and hasattr(self, '__modifiedfields__') and not key in self.__modifiedfields__:
            if self.pk or (self.pk is None and not value is None):
                self.__modifiedfields__.append(key)
        Model._setattr(self, key, value)

    models.Model.__init__ = __init__
    models.Model.delete = delete
    models.Model.save = save
    models.Model.__setattr__ = __setattr__
