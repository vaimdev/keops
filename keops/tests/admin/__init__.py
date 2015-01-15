from django.conf import settings
from django.test import TestCase, Client


class AdminTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_client(self):
        print(self.client.get('/admin/'))
