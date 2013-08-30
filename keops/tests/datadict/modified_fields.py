
from django.conf import settings
from django.test import TestCase

class ModifiedFieldsTestCase(TestCase):

    @staticmethod
    def setUpClass():
        # Enable log
        settings.DEBUG = True

    def test_modified_fields(self):
        from . import models
        from django.db import models as django
        obj = models.Person(first_name='John')
        print('Testing modified fields')
        print('Modified fields', obj._modified_fields)
        print('Saving object...')
        obj.save()
        print('Modified fields', obj._modified_fields)
        obj.last_name = 'Smith'
        print('Modified fields', obj._modified_fields)
        obj.first_name = 'John'
        print('Modified fields', obj._modified_fields)
        obj.last_name = 'Jordan'
        print('Modified fields', obj._modified_fields)
        obj.save()
        obj.last_name = 'Smith'
        print('Modified fields', obj._modified_fields)
        obj.save()
        obj.delete()
        print('Modified fields', obj._modified_fields)
        obj = models.Person(first_name='Peter', last_name='Erwin')
        obj.save()
        obj = models.Person.objects.get(pk=1)
        print('Modified fields', obj._modified_fields)
