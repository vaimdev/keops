
from django.conf import settings
from django.test import TestCase

class PerformanceTestCase(TestCase):

    @staticmethod
    def setUpClass():
        # Enable log
        settings.DEBUG = True

    def test_modified_fields(self):
        from . import models
        for m in models.Partner.objects.all():
            print(m)

# TODO: test foreignkey performance optimization
