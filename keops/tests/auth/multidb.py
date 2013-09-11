import json
from django.conf import settings
from django.test import TestCase, Client

class AuthTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

        # add test user
        from keops.modules.base import models
        u = models.User(username='test')
        u.set_password('test')
        u.save(using='default')

        cls.client2 = Client()


    def test_multi_db(self):
        from keops.modules.base import models
        # add db2 alias
        dbs = settings.DATABASES
        dbs['db2'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'USER': 'postgres',
            'SCHEMA': '',
            'PASSWORD': '1',
            'HOST': 'localhost',
            'PORT': '',
        }
        self.settings(DATABASES=dbs)
        from keops.db import scripts
        scripts.syncdb('db2')

        u = models.User(username='test')
        u.set_password('db2testpwd')
        u.save(using='db2')

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
        # CREATE
        company = {'model': 'base.company', 'data': json.dumps({'name': 'My test company on default alias'})}
        response = self.client.post('/db/submit/', company)
        assert response.status_code == 200

        company = {'model': 'base.company', 'data': json.dumps({'name': 'My test company on db2 alias'})}
        response = self.client2.post('/db/submit/', company)
        assert response.status_code == 200

        # Check data exists
        # READ
        cp1 = models.Company.objects.using('default').get(name='My test company on default alias')
        cp2 = models.Company.objects.using('db2').get(name='My test company on db2 alias')

        # UPDATE
        company = {'model': 'base.company', 'pk': cp1.pk, 'data': json.dumps({'name': 'default alias'})}
        response = self.client.post('/db/submit/', company)
        assert response.status_code == 200

        company = {'model': 'base.company', 'pk': cp2.pk, 'data': json.dumps({'name': 'db2 alias'})}
        response = self.client2.post('/db/submit/', company)
        assert response.status_code == 200

        # DELETE
        cp1 = models.Company.objects.using('default').get(name='default alias')
        cp2 = models.Company.objects.using('db2').get(name='db2 alias')

        response = self.client.delete('/db/submit/?model=base.company&pk=%d' % cp1.pk)
        assert response.status_code == 200

        response = self.client2.delete('/db/submit/?model=base.company&pk=%d' % cp2.pk)
        assert response.status_code == 200

    def test_related(self):
        from keops.modules.base import models
        # test related data
        company = {'model': 'base.company', 'data': json.dumps({'name': 'My test company on default alias'})}
        response = self.client.post('/db/submit/', company)
        assert response.status_code == 200
        cp1 = models.Company.objects.using('default').get(name='My test company on default alias')

        u = models.User.objects.using('default').get(username='test')
        admin = models.User.objects.using('default').get(username='admin')
        company = {
            'model': 'base.company',
            'pk': cp1.pk,
            'related': json.dumps([
                {
                    'model': 'base.element_users',
                    'linkField': 'element_id',
                    'data': [
                        {
                            'action': 'CREATE', 'data': {'user_id': u.pk}
                        },
                        {
                            'action': 'CREATE', 'data': {'user_id': admin.pk}
                        }
                    ]
                }
            ])
        }
        response = self.client.post('/db/submit/', company)
        assert response.status_code == 200
        assert cp1.users.all().count() == 2

    def test_performance(self):
        # performance test
        response = self.client.get('/db/?alias=default&next=/admin/')
        assert response.status_code == 302
        # try to login
        response = self.client.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'admin', 'password': 'admin'})
        assert response.status_code == 302
        for i in range(100):
            company = {'model': 'base.company', 'data': json.dumps({'name': 'Company %d' % i})}
            response = self.client.post('/db/submit/', company)
            assert response.status_code == 200
