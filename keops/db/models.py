
from django.db import models
from django.db.models import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from .fields import *
from keops.forms.admin import ModelAdmin

models.options.DEFAULT_NAMES = models.options.DEFAULT_NAMES + ('display_fields',)

class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        admin = attrs.pop('Admin', None)
        new_class = super(ModelBase, cls).__new__(cls, name, bases, attrs)
        if not admin:
            admin = getattr(new_class, 'Admin', None)
        new_class.add_to_class('_admin', ModelAdmin(admin))
        return new_class

class AbstractModel(models.Model, metaclass=ModelBase):
    
    class Meta:
        abstract = True
        
    def __str__(self):
        # auto detect display field expression
        if hasattr(self._meta, 'display_fields'):
            d - self._meta.display_fields
        elif hasattr(self, '_admin'):
            d = self._admin.display_expression

        if isinstance(d, str):
            return str(eval(d, globals(), {'self': self}))
        elif isinstance(d, (list, tuple)):
            return ' - '.join([str(getattr(self, v)) for v in d])
        else:
            return super(AbstractModel, self).__str__()
        
class Model(AbstractModel):
    created_by = ForeignKey('base.User', related_name='+')
    created_on = DateTimeField()
    modified_by = ForeignKey('base.User', related_name='+')
    modified_on = DateTimeField()
    
    class Meta:
        abstract = True

def model_created(sender, **kwargs):
    pass

models.signals.class_prepared.connect(model_created)
