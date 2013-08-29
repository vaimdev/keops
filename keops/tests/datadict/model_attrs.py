
from django.test import TestCase

class ModelAttrsTestCase(TestCase):
    def test_model_attrs(self):
        from . import models
        print('Person display expression: %s' % str(models.Person.Extra.display_expression))
        print('Person printable_fields: %s' % str(models.Person.Extra.field_groups))
        print('Author display expression: %s' % str(models.Author.Extra.display_expression))
        print('Author printable_fields: %s' % str(models.Author.Extra.field_groups))
        print('Customer display expression: %s' % str(models.Customer.Extra.display_expression))
        print('Customer printable_fields: %s' % str(models.Customer.Extra.field_groups))
        print('Student display expression: %s' % str(models.Student.Extra.display_expression))
        print('Student printable_fields: %s' % str(models.Student.Extra.field_groups))

    def test_model_str(self):
        from . import models
        obj = models.Person(first_name='John', last_name='Smith')
        print(str(obj))
