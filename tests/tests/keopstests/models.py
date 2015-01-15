from keops.db import models


class Category(models.Model):
    name = models.CharField(null=False, help_text='Category name')

    class Meta:
        class Admin:
            pass


class Contact(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(null=False, help_text='Contact name')
    email = models.EmailField()
    type = models.CharField(choices=(('choice 1', 'Choice 1'), ('choice 2', 'Choice 2')), help_text='Contact type')
    enabled = models.BooleanField(help_text='Contact is enabled')
    birth_date = models.DateField(help_text='Contact birth date')
    notes = models.TextField(help_text='<b>Note</b> information')

    def name_email(self):
        return '%s <strong>%s</strong>' % (self.name, self.email)
    name_email.short_description = 'Nome e-mail'
    name.allow_tags = True

    class Meta:
        class Admin:
            list_display = ['name_email']
