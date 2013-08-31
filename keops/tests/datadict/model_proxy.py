
from django.conf import settings
from django.test import TestCase

class ModelProxyTestCase(TestCase):

    @staticmethod
    def setUpClass():
        # Enable log
        settings.DEBUG = True

    def test_modified_fields(self):
        from . import models
        p = models.Person(first_name='John', last_name='Smith')
        p.save()
        print('partner str', str(p))

        c = models.Company(first_name='example.com')
        c.employee = p
        c.save()
        print('company name', str(c), str(c.employee))

        for m in models.Partner.objects.all():
            print('Model proxy result', str(m))
        for m in models.Company.objects.all():
            print('Advanced proxy result', str(m))

# TODO: test foreignkey performance optimization
