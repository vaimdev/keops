# Active Data Dictionary for Django base field class
from bisect import bisect
from django.db import models

__all__ = ['CharField', 'BooleanField', 'DecimalField', 'MoneyField', 'ForeignKey', 'ImageField',
           'VirtualField', 'PropertyField', 'OneToManyField', 'get_model_url']


# Additional field attributes
models.Field.readonly = False
models.Field.virtual = False
models.Field.widget_attrs = None
models.Field.template_name = None


# Monkey-patch default django Field class
class _Field(object):
    def __init__(self, *args, **kwargs):
        # Change default field db null to true
        kwargs.setdefault('null', not (kwargs.get('primary_key', False) or isinstance(self, models.OneToOneField)))
        kwargs.setdefault('blank', kwargs['null'])
        if isinstance(self, models.BooleanField):
            kwargs.pop('null', None)
            kwargs.pop('blank', None)
        # Add custom_attrs to field
        self.readonly = kwargs.pop('readonly', False)
        models.Field.__init__(self, *args, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        if not hasattr(cls._meta, 'all_fields'):
            cls._meta.all_fields = []
            for b in cls.__bases__:
                if hasattr(b, '_meta') and hasattr(b._meta, 'all_fields') and not b._meta.abstract:
                    cls._meta.all_fields += b._meta.all_fields
        cls._meta.all_fields.insert(bisect(cls._meta.all_fields, self), self)
        # Register server-side on_change field event
        if hasattr(self, 'custom_attrs') and 'on_change' in self.custom_attrs:
            self.custom_attrs.setdefault('widget_attrs', {})['ng_change'] = 'fieldChangeCallback(\'%s\')' % name
        models.Field.contribute_to_class(self, cls, name, virtual_only=virtual_only)

    models.Field.__init__ = __init__
    models.Field.contribute_to_class = contribute_to_class


class CharField(models.CharField):
    """
    Store null on database char field when value is None.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 64)
        super(CharField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Return None if field value is an empty string.
        """
        return None if value == "" else value


class DecimalField(models.DecimalField):
    def __init__(self, verbose_name=None, max_digits=18, decimal_places=4, **kwargs):
        super(DecimalField, self).__init__(verbose_name=verbose_name, max_digits=max_digits,
                                           decimal_places=decimal_places, **kwargs)


class MoneyField(models.DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=18, decimal_places=4, **kwargs):
        super(MoneyField, self).__init__(verbose_name=verbose_name, name=name, max_digits=max_digits,
            decimal_places=decimal_places, **kwargs)


# Change default BooleanField to NullBooleanField
class BooleanField(models.NullBooleanField):
    pass


def get_model_url(cls):
    """
    Get action resource url from a model class.
    """
    from keops.modules.base import models
    meta = cls._meta
    action = models.Action.objects.get_by_model_name('%s.%s' % (meta.app_label, meta.model_name))
    if action:
        return action.get_absolute_url() + 'form/'
    else:
        return ''


def get_resource_url(field, *args, **kwargs):
    """
    Auto detect resource url from a foreignkey field.
    """
    if not hasattr(field, 'resource_url'):
        field.resource_url = get_model_url(field.rel.to)
    return field.resource_url

models.ForeignKey.get_resource_url = get_resource_url


# Change ForeignKey fields for business model
class ForeignKey(models.ForeignKey):
    def __init__(self, to, to_field=None, rel_class=models.ManyToOneRel, db_constraint=True, **kwargs):
        # Protect foreign key delete cascade
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '+')
        super(ForeignKey, self).__init__(to=to, to_field=to_field, rel_class=rel_class, db_constraint=db_constraint, **kwargs)


class VirtualField(models.Field):
    """
    Provides a generic virtual field.
    """

    def __init__(self, verbose_name=None, help_text=None, blank=None, editable=True, **options):
        self.rel = None
        options.setdefault('readonly', True)
        super(VirtualField, self).__init__(
            verbose_name=verbose_name,
            help_text=help_text,
            blank=blank,
            editable=editable,
            **options)

    def contribute_to_class(self, cls, name):
        super(VirtualField, self).contribute_to_class(cls, name, True)
        setattr(cls, name, self)


class PropertyField(VirtualField):
    """
    Provides a virtual field based on property/function/expression.
    """

    def __init__(self, verbose_name=None, fget=None, fset=None, **options):
        self.fget = fget
        self.fset = fset
        options.setdefault('null', True)
        options.setdefault('blank', True)
        super(PropertyField, self).__init__(verbose_name=verbose_name, **options)

    def __get__(self, instance, instance_type=None):
        if instance_type == type:
            return self
        if self.fget:
            try:
                if isinstance(self.fget, str):
                    v = eval(self.fget, globals(), {'self': instance})
                elif callable(self.fget):
                    v = self.fget(instance)
                else:
                    v = self.fget
            except:
                return ''
            return str(v)

    def __set__(self, instance, value):
        if self.fset:
            self.fset(instance, value)


class OneToManyField(VirtualField):
    """
    Provides a one-to-many field representation.
    """

    def __init__(self, related_name, to=None, to_field=None, pk_field=None, list_fields=None, **options):
        self.related_name = related_name
        self.to = to
        self.to_field = to_field
        self.pk_field = pk_field
        self._descriptor = None
        self._related = None
        self._list_fields = list_fields
        self._choices = None
        options.setdefault('default', models.NOT_PROVIDED)
        super(OneToManyField, self).__init__(**options)

    def contribute_to_class(self, cls, name):
        super(OneToManyField, self).contribute_to_class(cls, name)
        if self.pk_field is None:
            self.pk_field = cls._meta.pk
        elif isinstance(self.pk_field, str):
            self.pk_field = cls._meta.get_field(self.pk_field)

    @property
    def descriptor(self):
        if self._descriptor is None and self.related_name:
            self._descriptor = getattr(self.model, self.related_name)
        return self._descriptor

    @property
    def list_fields(self):
        if not self._list_fields:
            self._list_fields = self.related.model._meta.admin.field_groups.get('list_fields') or\
                [f.name for f in self.related.model._meta.concrete_fields\
                 if not f.primary_key and not f is self.related.field]
        return self._list_fields

    @property
    def related(self):
        if self._related is None and self.related_name:
            self._related = self.descriptor.related
        return self._related

    def formfield(self, **kwargs):
        from keops.forms import GridField
        defaults = {'form_class': GridField, 'queryset': None}
        defaults.update(kwargs)
        return super(OneToManyField, self).formfield(**defaults)

    def __get__(self, instance, instance_type=None):
        if isinstance(instance, models.Model):
            return getattr(instance, self.related_name, None)
        else:
            return self
