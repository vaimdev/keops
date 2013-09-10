import json
from django.conf import settings
from django.test import TestCase, Client

class AuthTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def setUp(self):
        self.client = Client()

        # add test user
        from keops.modules.base import models
        u = models.User(username='test')
        u.set_password('test')
        u.save()

        self.client2 = Client()

        # add db2 alias
        dbs = settings.DATABASES
        dbs['db2'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'my_db',
            'USER': 'postgres',
            'SCHEMA': '',
            'PASSWORD': '1',
            'HOST': 'localhost',
            'PORT': '',
        }
        self.settings(DATABASES=dbs)
        from keops.db import scripts
        scripts.recreatedb('db2')
        scripts.syncdb('db2')

        u = models.User(username='test')
        u.set_password('db2testpwd')
        u.save(using='db2')

    def test_multi_db(self):
        response = self.client.get('/db/?alias=default')
        assert response.status_code == 200
        assert response.content == b'default'
        response = self.client.get('/db/?alias=default&next=/admin/')
        assert response.status_code == 302
        # try to login
        response = self.client.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'admin', 'password': 'admin'})
        assert response.status_code == 302

        # test db2 alias
        response = self.client2.get('/db/?alias=db2')
        assert response.status_code == 200
        assert response.content == b'db2'
        response = self.client2.get('/db/?alias=db2&next=/admin/')
        # must redirect to login
        assert response.status_code == 302
        # try to login
        response = self.client2.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'admin', 'password': 'admin'})
        assert response.status_code == 302
        response = self.client2.get(settings.LOGOUT_URL)
        response = self.client2.get('/db/?alias=db2&next=/admin/')
        # try invalid login
        response = self.client2.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'test', 'password': 'test'})
        assert response.status_code == 200
        # try login
        response = self.client2.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'test', 'password': 'db2testpwd'})
        assert response.status_code == 302
        response = self.client.get('/db/')
        assert response.content == b'default'
        response = self.client2.get('/db/')
        assert response.content == b'db2'

        # CRUD tests
        company = {'model': 'base.company', 'data': json.dumps({'name': 'My test company on default alias'})}
        response = self.client.post('/db/submit/', company)
        assert response.status_code == 200

        company = {'model': 'base.company', 'data': json.dumps({'name': 'My test company on db2 alias'})}
        response = self.client2.post('/db/submit/', company)
        assert response.status_code == 200

        # Check data exists
        from keops.modules.base import models
        models.Company.objects.using('default').get(name='My test company on default alias')
        models.Company.objects.using('db2').get(name='My test company on db2 alias')
