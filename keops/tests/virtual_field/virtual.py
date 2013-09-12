from django.test import TestCase

class VirtualFieldTestCase(TestCase):

    def test_virtual_field(self):
        from . import models
        r = models.TestModel()
        r.save()
        print(r.field2)
