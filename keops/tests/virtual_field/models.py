from keops.db import models

class TestModel(models.Model):
    field1 = models.CharField()

    def get_field2(self):
        return 'Field2 value'

    def set_field2(self, value):
        self._field2 = value
        print('set virtual field2 value')

    field2 = models.PropertyField(fget=get_field2, fset=set_field2)

class Master(models.Model):
    name = models.CharField(blank=False)
    details = models.OneToManyField(related_name='detail_set')

class Detail(models.Model):
    parent = models.ForeignKey(Master, null=False)
    name = models.CharField(blank=False)
    description = models.CharField()
