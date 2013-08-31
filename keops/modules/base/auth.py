
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from django.contrib.auth import models as auth

class User(auth.AbstractUser):
    email_signature = models.TextField(_('e-mail signature'))
    report_signature = models.TextField(_('report signature'))
    
    class Meta:
        db_table = 'auth_user'
