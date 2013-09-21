import json
from django.test import TestCase, Client

class ClientTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def setUp(self):
        self.client = Client()

    def test_get(self):
        from . import models
        m = models.Master(name='master 2')
        m.save()
        models.Detail.objects.create(name='master 1/detail 1', parent=m)
        response = self.client.get('/db/grid/?model=virtual_field.master&field=details&pk=%d' % m.pk)
        data = json.loads(response.content.decode('utf-8'))
        models.Detail.objects.create(name='master 1/detail 2', parent=m)
        models.Detail.objects.create(name='master 1/detail 3', parent=m)
        models.Detail.objects.create(name='master 1/detail 4', parent=m)
        response = self.client.get('/db/grid/?model=virtual_field.master&field=details&pk=%d' % m.pk)
        data = json.loads(response.content.decode('utf-8'))

    def test_read_items(self):
        response = self.client.get('/db/read/items/?model=virtual_field.master&pk=1&items=["models1"]')
        print(response.content)
