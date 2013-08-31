
from keops.db import models

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
