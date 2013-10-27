from keops.db import models


class Model1(models.Model):

    class Admin:
        actions = ['action1']

        def action1(self, request, queryset):
            pass
