
from django.db import models

__all__ = ['CharField', 'BooleanField', 'DecimalField', 'MoneyField', 'ForeignKey']

# Add custom_attrs to field instances
class _Field(object):
    _init = models.Field.__init__

    def __init__(self, *args, **kwargs):
        self.custom_attrs = kwargs.pop('custom_attrs', {})
        _Field._init(self, *args, **kwargs)

    models.Field.__init__ = __init__

class NullCharField(models.CharField):
    """Stores null on database char field when value is none."""

    def to_python(self, value):
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Returns None if field value is an empty string."""
        return None if value == "" else value

class MoneyField(models.DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=18, decimal_places=4, **kwargs):
        super(MoneyField, self).__init__(verbose_name=verbose_name, name=name, max_digits=max_digits,
            decimal_places=decimal_places, **kwargs)

# Change default BooleanField to NullBooleanField
def BooleanField(*args, **options):
    return models.NullBooleanField(*args, **options)

# Change default CharField to NullCharField
def CharField(max_length=None, empty_null=True, *args, **options):
    if empty_null:
        return NullCharField(max_length, *args, **options)
    else:
        return models.CharField(max_length, **options)

# Decimal(12, 4) shortcut
def DecimalField(*args, **options):
    options.setdefault('max_digits', 12)
    options.setdefault('decimal_places', 4)
    return models.DecimalField(*args, **options)

# Change ForeignKey fields for business model
def ForeignKey(to, to_field=None, rel_class=models.ManyToOneRel,
                 db_constraint=True, **options):
    #list_display = options.pop('list_display', [])
    # Protect foreign key delete cascade
    options.setdefault('on_delete', models.PROTECT)
    f = models.ForeignKey(to=to, to_field=to_field, rel_class=rel_class, db_constraint=db_constraint, **options)
    #f.list_display = list_display
    return f
