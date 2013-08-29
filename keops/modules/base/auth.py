
from django.utils.translation import ugettext_lazy as _
from keops.db import models
from django.contrib.auth import models as auth

class User(auth.AbstractUser):
    email_signature = models.TextField(_('E-mail Signature'))
    report_signature = models.TextField(_('Report Signature'))
    
    class Meta:
        db_table = 'auth_user'
