from django.test import TestCase

class FixturesTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def test_fixtures(self):
        from keops.modules.base import models
        for m in models.Menu.objects.all():
            str(m)

    def test_base_crud(self):
        from keops.modules.base import models
        c = models.Company(name='My test company')
        c.save()
        c = models.Company(name='My test company 2')
        c.save()
        c.name = 'My Company 2'
        c.save()
        c.delete()
