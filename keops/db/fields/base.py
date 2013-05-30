
from django.db import models
from . import bigint

class CharNullField(models.CharField):
    """Stores null on database char field value."""

    def to_python(self, value):
        return value
        
    def get_db_prep_value(self, value, connection, prepared):
        if value == "":
            return None
        else:
            return value

class Field(models.Field):
    def __init__(self, **kwargs):
        attrs = get_field_props(self.__class__, kwargs)
        super(Field, self).__init__(**kwargs)
        set_field_props(self, attrs)

def get_field_props(cls, kwargs):
    attrs = {}
    kwargs.setdefault('null', not kwargs.get('primary_key', False))
    kwargs.setdefault('blank', kwargs['null'])
    attrs['update_default'] = kwargs.pop('update_default', models.NOT_PROVIDED)
    attrs['page'] = kwargs.pop('page', None)
    attrs['fieldset'] = kwargs.pop('fieldset', None)
    attrs['empty_text'] = kwargs.pop('empty_text', None)
    #attrs['limit_choices_to'] = kwargs.pop('limit_choices_to', None)
    attrs['mask_re'] = kwargs.pop('mask_re', None)
    attrs['visible'] = kwargs.pop('visible', True)
    attrs['readonly'] = kwargs.pop('readonly', 'formula' in kwargs)
    attrs['formula'] = kwargs.pop('formula', None)
    attrs['mask'] = kwargs.pop('mask', None)
    attrs['summary'] = kwargs.pop('summary', None)
    attrs['printable'] = kwargs.pop('printable', attrs['visible'])
    attrs['attrs'] = kwargs.pop('attrs', None)
    attrs['group_field'] = kwargs.pop('group_field', None)
    attrs['widget'] = kwargs.pop('widget', None)
    attrs['custom_attrs'] = kwargs.pop('custom_attrs', {})
    return attrs
        
def _prepare_field(cls, *args, **kwargs):
    attrs = get_field_props(cls, kwargs)
    f = cls(*args, **kwargs)
    set_field_props(f, attrs)
    return f
    
def set_field_props(f, attrs):
    f.custom_attrs = attrs.pop('custom_attrs')
    f.custom_attrs.update(attrs)

def BooleanField(*args, **kwargs):
    #kwargs.setdefault('widget', 'BooleanField')
    return _prepare_field(models.NullBooleanField, *args, **kwargs)

def CharField(*args, **kwargs):
    #kwargs.setdefault('widget', 'TextField')
    return _prepare_field(CharNullField, *args, **kwargs)

def DateField(*args, **kwargs): 
    #kwargs.setdefault('widget', 'DateField')
    return _prepare_field(models.DateField, *args, **kwargs)

def DateTimeField(*args, **kwargs):
    #kwargs.setdefault('widget', 'DateTimeField')
    return _prepare_field(models.DateTimeField, *args, **kwargs)

def DecimalField(*args, **kwargs):
    kwargs.setdefault('max_digits', 18)
    kwargs.setdefault('decimal_places', 4)
    return _prepare_field(models.DecimalField, *args, **kwargs)

def CurrencyField(*args, **kwargs):
    kwargs.setdefault('max_digits', 18)
    kwargs.setdefault('decimal_places', 4)
    return _prepare_field(models.DecimalField, *args, **kwargs)

MoneyField = CurrencyField

def FloatField(*args, **kwargs):
    return _prepare_field(models.FloatField, *args, **kwargs)

def ForeignKey(*args, **kwargs):
    list_display = kwargs.pop('list_display', [])
    # Protect foreign key delete cascade
    kwargs.setdefault('on_delete', models.PROTECT)
    obj = _prepare_field(models.ForeignKey, *args, **kwargs)
    obj.list_display = list_display
    return obj

def OneToOneField(*args, **kwargs):
    return _prepare_field(models.OneToOneField, *args, **kwargs)

def SmallIntegerField(*args, **kwargs):
    return _prepare_field(models.SmallIntegerField, *args, **kwargs)

def IntegerField(*args, **kwargs):
    return _prepare_field(models.IntegerField, *args, **kwargs)

def BigIntegerField(*args, **kwargs):
    return _prepare_field(bigint.BigIntegerField, *args, **kwargs)

def TextField(*args, **kwargs):
    return _prepare_field(models.TextField, *args, **kwargs)

def TimeField(*args, **kwargs):
    kwargs.setdefault('widget', 'TimeField')
    return _prepare_field(models.TimeField, *args, **kwargs)

def ManyToManyField(*args, **kwargs):
    return _prepare_field(models.ManyToManyField, *args, **kwargs)

def AutoField(*args, **kwargs):
    return _prepare_field(models.AutoField, primary_key=True, *args, **kwargs)

def EmailField(*args, **kwargs):
    return _prepare_field(models.EmailField, *args, **kwargs)

def FileField(*args, **kwargs):
    return _prepare_field(models.FileField, *args, **kwargs)

def ImageFileField(*args, **kwargs):
    return _prepare_field(models.ImageField, *args, **kwargs)

def URLField(*args, **kwargs):
    return _prepare_field(models.URLField, *args, **kwargs)

def PositiveIntegerField(*args, **kwargs):
    return _prepare_field(models.PositiveIntegerField, *args, **kwargs)

def BinaryField(*args, **kwargs):
    return _prepare_field(models.BinaryField, *args, **kwargs)

def ImageField(*args, **kwargs):
    return _prepare_field(models.FileField, *args, **kwargs)
