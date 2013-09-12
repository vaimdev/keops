from django.test import TestCase

class VirtualFieldTestCase(TestCase):

    def test_virtual_field(self):
        from . import models
        r = models.TestModel()
        r.save()
        print(r.field2)

    def test_one_to_many(self):
        from . import models
        m = models.Master(name='master 1')
        m.save()
        models.Master.objects.create(name='master 2')

        d = models.Detail(name='master 1/detail 1', parent=m)
        d.save()
        d = models.Detail(name='master 1/detail 2', parent=m)
        d.save()

        for d in m.details.all():
            print('Print detail', d)
