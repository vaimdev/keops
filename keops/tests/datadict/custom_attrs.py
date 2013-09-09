from django.test import TestCase

class CustomAttrsTestCase(TestCase):

    def test_custom_attrs(self):
        from keops.modules.base import models
        print('Field custom_attrs: %s' % str(models.Action._meta.get_field('name').custom_attrs))
