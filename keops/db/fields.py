# Active Data Dictionary for Django base field class
from django.conf import settings
from django.db import models

__all__ = ['CharField', 'BooleanField', 'DecimalField', 'MoneyField', 'ForeignKey', 'FileRelField', 'ImageRelField']

FIELD_BASIC_SEARCH = "basic"
FIELD_ADVANCED_SEARCH = "advanced"

# Add custom_attrs to field instances
# custom_attrs items:
#   widget -> field widget type (extjs compatible widgets)
#   page -> field will be placed on specified page
#   fieldset -> field will be placed on specified fieldset
#   mask -> field widget input mask
#   on_change -> on field change event
#   dependencies -> field dependencies
#   client_formula -> field client side formula
#   server_formula -> field server side formula
#   client_attrs -> client side widget attributes as javascript expression, dict or list object: {'visible': 'this.fieldValue("field") == true'}
#   server_attrs -> server side widget attributes as python expression, callable, dict or list object: {'visible': 'self.field is None'}
#   states -> on server side, this attribute configure target field state: {'object state': 'field_attr = value'}
#   change_default -> if user can change field default value
#   insert_default -> default value for new objects
#   update_default -> default value for updated objects
#   translate -> field content translation (True/False)
#   select -> field search type: None = no search, "basic" = basic search, "advanced" = advanced filter
#   widget_attrs -> client side widget attributes (all extjs compatible attributes are supported)
class Field(object):
    _init = models.Field.__init__

    def __init__(self, *args, **kwargs):
        # Change default field db null to false
        if not isinstance(self, models.BooleanField):
            kwargs.setdefault('null', not (kwargs.get('primary_key', False) or isinstance(self, models.OneToOneField)))
        # Add custom_attrs to field
        self.custom_attrs = kwargs.pop('custom_attrs', {})
        self.readonly = kwargs.pop('readonly', False)
        Field._init(self, *args, **kwargs)

    models.Field.__init__ = __init__

class NullCharField(models.CharField):
    """
    Store null on database char field when value is None.
    """

    def to_python(self, value):
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Return None if field value is an empty string.
        """
        return None if value == "" else value

class MoneyField(models.DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=18, decimal_places=4, **kwargs):
        super(MoneyField, self).__init__(verbose_name=verbose_name, name=name, max_digits=max_digits,
            decimal_places=decimal_places, **kwargs)

# Change default BooleanField to NullBooleanField
BooleanField = models.NullBooleanField

# Change default CharField to NullCharField
def CharField(verbose_name=None, max_length=100, empty_null=True, *args, **options):
    if empty_null:
        return NullCharField(verbose_name=verbose_name, max_length=max_length, *args, **options)
    else:
        return models.CharField(verbose_name=verbose_name, max_length=max_length, **options)

# Decimal(18, 4) shortcut
def DecimalField(*args, **options):
    options.setdefault('max_digits', 18)
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

class FileRelField(models.ForeignKey):
    """
    ForeignKey to store file field on a database binary column, the default model
    is specified on settings.FILE_FIELD_MODEL. This strategy will optimize performance,
    once binary data will be loaded when fk is invoked manually.
    """
    def __init__(self, to=None, to_field=None, rel_class=models.ManyToOneRel,
                 db_constraint=True, **options):
        if to is None and hasattr(settings, 'FILE_FIELD_MODEL'):
            to = settings.FILE_FIELD_MODEL
        options.setdefault('related_name', '+')
        super(FileRelField, self).__init__(to=to, to_field=to_field, rel_class=rel_class,
                                           db_constraint=db_constraint, **options)

class ImageRelField(FileRelField):
    pass

# TODO: add ImageRelField (a foreign key to file model), to performance optimization binary content load
# TODO: optimize foreignkey queryset
# The foreignkey field default queryset selects all fields, specifying automatically only needed/representation fields
