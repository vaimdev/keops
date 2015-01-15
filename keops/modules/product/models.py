from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from keops.modules.base.models import CompanyModel


class UnitCategory(models.Model):
    name = models.CharField(null=False, db_index=True)


class Unit(models.Model):
    TYPE = (
        ('reference', _('Referenced unit for this category')),
        ('bigger', _('Bigger than the referenced unit')),
        ('smaller', _('Smaller than the references unit')),
    )
    name = models.CharField(null=False, db_index=True)
    type = models.CharField(max_length=16, choices=TYPE, null=False)
    ratio = models.FloatField(_('ratio'), default='reference')
    rounding = models.FloatField(_('rouding'))
    category = models.ForeignKey(UnitCategory)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Product Unit of Measure')
        verbose_name_plural = _('Product Units of Measure')


class Item(CompanyModel):
    TYPE = (
        ('C', _('Consumable')),
        ('S', _('Service')),
    )
    STATE = (
        ('draft', _('Draft/In Development')),
        ('production', _('Production/Normal')),
        ('end', _('End of Lifecycle')),
        ('obsolete', _('Obsolete')),
    )
    MEASURE_TYPE = (
        ('fixed', _('Fixed')),
        ('variable', _('Variable')),
    )
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField()
    category = models.ForeignKey(Category)
    unit = models.ForeignKey(Unit)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL)
    type = models.CharField(max_length=16, choices=TYPE)
    rental = models.BooleanField(default=False)
    state = models.CharField(max_length=16, choices=STATE)
    coefficient = models.FloatField()
    measure_type = models.CharField(choices=MEASURE_TYPE)
    active = models.BooleanField(default=True)


class Product(Item):
    qty_available = models.FloatField()
    qty_virtual = models.FloatField()


class Package(models.Model):
    name = models.CharField(db_index=True)
    sequence = models.PositiveIntegerField()
    product = models.ForeignKey(Product, null=False)


class Category(models.Model):
    name = models.CharField(db_index=True)
    description = models.CharField(max_length=128)
    parent = models.ForeignKey('self')
    sequence = models.PositiveIntegerField()
