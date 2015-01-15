from keops.db import models


class Model1(models.Model):
    codigo = models.CharField('Código')

    class Meta:
        class Admin:
            pass


class Model2(Model1):
    nome = models.CharField('Nome')

    class Meta:
        class Admin:
            default_fields = ['id']
