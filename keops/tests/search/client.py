from django.conf import settings
from django.test import TestCase, Client

class SearchTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def setUp(self):
        # add test user
        from keops.modules.base import models
        u = models.User(username='test')
        u.set_password('test')
        u.save()
        self.client = Client()

    def test_admin_index(self):
        response = self.client.get('/admin/')
        # /admin/ have to redirect
        self.assertRedirects(response, settings.LOGIN_URL + '?next=/admin/')
        # try to login
        response = self.client.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'admin', 'password': 'admin'})
        assert response.status_code == 302
        response = self.client.get(settings.LOGOUT_URL)

        response = self.client.get('/admin/')
        self.assertRedirects(response, settings.LOGIN_URL + '?next=/admin/')
        response = self.client.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'test', 'password': 'test'})
