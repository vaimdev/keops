
from django.db import models
from .fields import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from keops.forms.admin import ModelAdmin
from django.db.models import *

models.options.DEFAULT_NAMES = models.options.DEFAULT_NAMES + ('display_expression',)

class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        admin = attrs.pop('Admin', None)
        new_class = super(ModelBase, cls).__new__(cls, name, bases, attrs)
        if not admin:
            admin = getattr(new_class, 'Admin', None)
        new_class.add_to_class('_admin', ModelAdmin(admin))
        return new_class

class Model(models.Model, metaclass=ModelBase):
    
    class Meta:
        abstract = True
        
    def __str__(self):
        # auto detect display field expression
        if hasattr(self._meta, 'display_expression'):
            d = self._meta.display_expression
        elif hasattr(self, '_admin'):
            d = self._admin.display_expression

        if isinstance(d, str):
            return str(eval(d, globals(), {'self': self}))
        elif isinstance(d, (list, tuple)):
            return ' - '.join([str(getattr(self, v)) for v in d])
        else:
            return super(Model, self).__str__()
