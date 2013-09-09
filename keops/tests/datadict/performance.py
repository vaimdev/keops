
from django.conf import settings
from django.test import TestCase

class PerformanceTestCase(TestCase):

    @staticmethod
    def setUpClass():
        # Enable log
        settings.DEBUG = True

    def test_crud(self):
        self._crud()

    def _crud(self):
        from . import models
        # Simple model
        self._create(models.Model1)
        self._read(models.Model1)
        self._update(models.Model1)
        self._delete(models.Model1)

        # Inherited model
        self._create(models.Customer)
        self._read(models.Customer)
        self._update(models.Customer)
        self._delete(models.Customer)

    def _create(self, model):
        f = open(__file__, 'rb')
        for i in range(100):
            p = model()
            p.field1 = 'Row %d' % i
            p.field3 = f.read()
            p.x = 1
            p.save()

    def _read(self, model):
        for r in model.objects.all():
            r.field1

    def _update(self, model):
        for r in model.objects.all():
            r.field2 = b'field 2 value'
            r.save()

    def _delete(self, model):
        for r in model.objects.all():
            r.delete()

# TODO: test foreignkey performance optimization
