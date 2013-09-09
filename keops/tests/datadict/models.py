
from keops.db import models

class Model1(models.Model):
    field1 = models.CharField()
    field2 = models.BinaryField()
    field3 = models.BinaryField()
    field4 = models.BinaryField()
    field5 = models.BinaryField()
    field6 = models.BinaryField()
    field7 = models.BinaryField()
    field8 = models.BinaryField()
    field9 = models.BinaryField()
    field10 = models.BinaryField()
    field11 = models.BinaryField()
    field12 = models.BinaryField()
    field13 = models.BinaryField()
    field14 = models.BinaryField()
    field15 = models.BinaryField()
    field16 = models.BinaryField()
    field17 = models.BinaryField()
    field18 = models.BinaryField()
    field19 = models.BinaryField()
    field20 = models.BinaryField()
    field21 = models.BinaryField()
    field22 = models.BinaryField()
    field23 = models.BinaryField()
    field24 = models.BinaryField()
    field25 = models.BinaryField()
    field26 = models.BinaryField()
    field27 = models.BinaryField()
    field28 = models.BinaryField()
    field29 = models.BinaryField()
    field30 = models.BinaryField()
    field31 = models.BinaryField()
    field32 = models.BinaryField()


class Person(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()

    class Extra:
        display_expression = ('first_name', 'last_name')
        field_groups = {
            'printable_fields': ['first_name', 'other_field']
        }

        def before_save(self, *args, **kwargs):
            print('Before save -> %s - ID: %s' % (str(self), self.pk))

        def before_change(self, *args, **kwargs):
            print('Before change -> %s - ID: %s' % (str(self), self.pk))

        def before_insert(self, *args, **kwargs):
            print('Before insert -> %s - ID: %s' % (str(self), self.pk))

        def before_update(self, *args, **kwargs):
            print('Before update -> %s - ID: %s' % (str(self), self.pk))

        def before_delete(self, *args, **kwargs):
            print('Before delete -> %s - ID: %s' % (str(self), self.pk))

        def after_save(self, *args, **kwargs):
            print('After save -> %s - ID: %s' % (str(self), self.pk))

        def after_change(self, *args, **kwargs):
            print('After change -> %s - ID: %s' % (str(self), self.pk))

        def after_insert(self, *args, **kwargs):
            print('After insert -> %s - ID: %s' % (str(self), self.pk))

        def after_update(self, *args, **kwargs):
            print('After update -> %s - ID: %s' % (str(self), self.pk))

        def after_delete(self, *args, **kwargs):
            print('After delete -> %s - ID: %s' % (str(self), self.pk))

    def __str__(self):
        return str(self.last_name)

class Author(Person):
    reference = models.CharField()

class Customer(Person):
    reference = models.CharField()

    class Extra:
        pass

class Student(Person):
    new_field = models.CharField()

    class Extra(Person.Extra):
        display_expression = Person.Extra.display_expression + ('new_field',)

class Partner(Person):
    reference = models.BooleanField()

    class Meta:
        proxy = True

# Very advanced model inheritance
class Company(Partner):
    address = models.TextField()
    employee = models.ForeignKey(Person)

    class Meta:
        proxy = True
