
# Include field data dictionary attributes

from django.db import models

class Field(models.Field):
    def __init__(self, **kwargs):
        attrs = get_field_props(self.__class__, kwargs)
        super(Field, self).__init__(**kwargs)
        set_field_props(self, attrs)

class CharNullField(models.CharField):
    """Stores null on database char field value."""

    def to_python(self, value):
        return value

    def get_db_prep_value(self, value, connection, prepared):
        """Returns None if field value is an empty string."""
        if value == "":
            return None
        else:
            return value

def AutoField(*args, **kwargs):
    return _prepare_field(models.AutoField, primary_key=True, *args, **kwargs)

def BigIntegerField(**options):
    return _prepare_field(models.BigIntegerField, **options)

def BooleanField(*args, **kwargs):
    return _prepare_field(models.NullBooleanField, *args, **kwargs)

def CharField(max_length=None, **kwargs):
    return _prepare_field(CharNullField, max_length, **kwargs)

def CommaSeparatedIntegerField(*args, **kwargs):
    return _prepare_field(models.CommaSeparatedIntegerField, *args, **kwargs)

def DateField(auto_now=False, auto_now_add=False, **options):
    return _prepare_field(models.DateField, auto_now, auto_now_add, **options)

def DateTimeField(auto_now=False, auto_now_add=False, **options):
    return _prepare_field(models.DateTimeField, auto_now, auto_now_add, **options)

def DecimalField(max_digits=None, decimal_places=None, **options):
    return _prepare_field(models.MoneyField, max_digits, decimal_places, **options)

def EmailField(max_length=75, **options):
    return _prepare_field(models.EmailField, max_length, **options)

def FileField(*args, **kwargs):
    return _prepare_field(models.FileField, *args, **kwargs)

def FilePathField(path=None, match=None, recursive=False, max_length=100, **options):
    return _prepare_field(models.FilePathField, path, match, recursive, max_length, **options)

def FloatField(*args, **kwargs):
    return _prepare_field(models.FloatField, *args, **kwargs)

def ImageField(*args, **kwargs):
    return _prepare_field(models.FileField, *args, **kwargs)

def ImageFileField(*args, **kwargs):
    return _prepare_field(models.ImageField, *args, **kwargs)

def IntegerField(*args, **kwargs):
    return _prepare_field(models.IntegerField, *args, **kwargs)

def IPAddressField(*args, **kwargs):
    return _prepare_field(models.IPAddressField, *args, **kwargs)

def GenericIPAddressField(**options):
    return _prepare_field(models.GenericIPAddressField, **options)

def MoneyField(max_digits=18, decimal_places=4, **options):
    return _prepare_field(models.MoneyField, max_digits, decimal_places, **options)

def PositiveIntegerField(*args, **kwargs):
    return _prepare_field(models.PositiveIntegerField, *args, **kwargs)

def PositiveSmallIntegerField(*args, **kwargs):
    return _prepare_field(models.PositiveSmallIntegerField, *args, **kwargs)

def SmallIntegerField(*args, **kwargs):
    return _prepare_field(models.SmallIntegerField, *args, **kwargs)

def SlugField(max_length=50, **options):
    return _prepare_field(models.SlugField, max_length, **options)

def TextField(*args, **kwargs):
    return _prepare_field(models.TextField, *args, **kwargs)

def TimeField(*args, **kwargs):
    kwargs.setdefault('widget', 'TimeField')
    return _prepare_field(models.TimeField, *args, **kwargs)

def URLField(*args, **kwargs):
    return _prepare_field(models.URLField, *args, **kwargs)


# Relationship fields


def ForeignKey(othermodel, **options):
    list_display = options.pop('list_display', [])
    # Protect foreign key delete cascade
    options.setdefault('on_delete', models.PROTECT)
    obj = _prepare_field(models.ForeignKey, othermodel, **options)
    obj.list_display = list_display
    return obj

def ManyToManyField(othermodel, **kwargs):
    return _prepare_field(models.ManyToManyField, othermodel, **kwargs)

def OneToOneField(othermodel, parent_link=False, **options):
    return _prepare_field(models.OneToOneField, othermodel, parent_link, **options)

def get_field_attrs(cls, kwargs):
    """Returns field data dictionary attributes."""
    attrs = {}
    kwargs.setdefault('null', not kwargs.get('primary_key', False))
    kwargs.setdefault('blank', kwargs['null'])
    attrs['update_default'] = kwargs.pop('update_default', models.NOT_PROVIDED)
    attrs['page'] = kwargs.pop('page', None)
    attrs['fieldset'] = kwargs.pop('fieldset', None)
    attrs['empty_text'] = kwargs.pop('empty_text', None)
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
    attrs = get_field_attrs(cls, kwargs)
    f = cls(*args, **kwargs)
    set_field_props(f, attrs)
    return f

def set_field_props(f, attrs):
    f.custom_attrs = attrs.pop('custom_attrs')
    f.custom_attrs.update(attrs)
