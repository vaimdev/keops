from django.conf import settings
from django.test import TestCase


class AdminTestCase(TestCase):
    def test_admin(self):
        from .models import Model1
        print(Model1._admin.actions)
        print(Model1._admin.action1)
