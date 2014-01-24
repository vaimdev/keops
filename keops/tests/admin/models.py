from django.db import models

class Model1(models.Model):
    codigo = models.CharField('Código')

    class Meta:
        class Admin:
            default_fields = ['field1', 'field2']


class Model2(Model1):
    nome = models.CharField('Nome')

    class Meta:
        pass
