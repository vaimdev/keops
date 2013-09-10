from django.test import TestCase, Client

class BaseSessionTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def setUp(self):
        self.client = Client()

    def test_session(self):
        session = self.client.session
        session['key 1'] = 'value 1'
        response = self.client.get('/admin/')

