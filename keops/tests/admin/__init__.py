from django.conf import settings
from django.test import TestCase


class AdminTestCase(TestCase):

    def test_admin(self):
        from .models import Model1
        print(Model1._admin.get_list_display(None))
        print(Model1._admin.get_search_fields(None))
        print(Model1._admin)

