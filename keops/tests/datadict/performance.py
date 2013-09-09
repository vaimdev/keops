
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
        self._create()
        self._read()
        self._update()
        self._delete()

    def _create(self):
        from . import models
        f = open(__file__, 'rb')
        for i in range(100):
            p = models.Model1()
            p.field1 = 'Row %d' % i
            p.field3 = f.read()
            p.x = 1
            p.save()

    def _read(self):
        from . import models
        for r in models.Model1.objects.all():
            print('Read', r.field1)

    def _update(self):
        from . import models
        for r in models.Model1.objects.all():
            r.field2 = b'field 2 value'
            r.save()

    def _delete(self):
        from . import models
        for r in models.Model1.objects.all():
            r.delete()

# TODO: test foreignkey performance optimization
