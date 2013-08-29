
from django.test import TestCase

class ModifiedFieldsTestCase(TestCase):
    def test_modified_fields(self):
        from . import models
        obj = models.Person(first_name='John')
        print('Testing modified fields')
        print('Modified fields', obj.__modifiedfields__)
        obj.save()
        print('Modified fields', obj.__modifiedfields__)
        obj.last_name = 'Smith'
        print('Modified fields', obj.__modifiedfields__)
        obj.first_name = 'John'
        print('Modified fields', obj.__modifiedfields__)
        obj.last_name = 'Jordan'
        print('Modified fields', obj.__modifiedfields__)
