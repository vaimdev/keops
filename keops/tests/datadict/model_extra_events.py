
from django.test import TestCase

class ModelExtraEventsTestCase(TestCase):
    def test_model_events(self):
        from . import models
        obj = models.Person(first_name='John', last_name='Smith')
        print('Saving John Smith...')
        obj.save()
        print('John Smith saved!')
        print('John Smith ID: %s' % obj.pk)
        obj.last_name = 'Jordan'
        obj.save()
        print('Read object')
        obj = models.Person.objects.get(pk=1)
        obj.delete()
