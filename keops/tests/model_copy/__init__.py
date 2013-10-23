import copy
import json
from django.test import TestCase, Client

class ClientTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        from . import models
        m = models.Master(name='master 2')
        m.save()
        cp = copy.copy(m)
        cp.description = 'new master 2'
        cp.save()
        print(cp.pk, models.Master.objects.count())

    def test_client_copy(self):
        from . import models
        m = models.Master(name='master 2', description='master 2 description')
        m.save()
        response = self.client.get('/db/new/copy/?model=model_copy.master&pk=1')
        print(response.content)
