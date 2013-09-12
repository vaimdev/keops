from keops.db import models

class TestModel(models.Model):
    field1 = models.CharField()

    def get_field2(self):
        return 'Field2 value'

    def set_field2(self, value):
        self._field2 = value
        print('set virtual field value')

    field2 = models.PropertyField(fget=get_field2, fset=set_field2)
