from django.conf import settings
from django.test import TestCase


class AdminTestCase(TestCase):

    def test_admin(self):
        from django.contrib.auth.models import Group
        from .models import Model1, Model2
        print(Model1._meta.Admin, Model2._meta.Admin)
        print(Model1._meta.Admin.default_fields, Model2._meta.Admin.default_fields)
        print(Model1._meta.admin.field_groups, Model2._meta.admin.field_groups)
        print('group', Group._meta.admin.field_groups)
        print('group', Group._meta.admin.model_admin)
