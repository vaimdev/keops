
from django.test import TestCase

class FixturesTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def test_fixtures(self):
        from keops.modules.base import models
        for m in models.Menu.objects.all():
            print(m)
