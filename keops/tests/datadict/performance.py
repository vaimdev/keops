
from django.conf import settings
from django.test import TestCase

class PerformanceTestCase(TestCase):

    @staticmethod
    def setUpClass():
        # Enable log
        settings.DEBUG = True

    def test_modified_fields(self):
        from keops.modules.base import models as base
        modules = base.Module.objects.all()
        for m in modules:
            print('Module:', str(m))
        models = base.BaseModel.objects.all()
        for m in models:
            print('Model:', str(m))

# TODO: test foreignkey performance optimization
