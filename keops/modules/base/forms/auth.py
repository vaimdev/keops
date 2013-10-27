from django.utils.translation import ugettext_lazy as _
from django import forms
from keops.db import models
from keops.forms.admin.models import ModelAdmin
from keops.modules.base import auth

class UserAdmin(ModelAdmin):
    model = auth.User
    default_admin = True
    pages = (
        (None, (
            (None, {
                'fields': (
                    'username', 'name', 'email', 'is_staff', 'is_active', 'date_joined', 'last_login'
                )
            }),
        ),),
        (_('Permissions'), (
            (None, {'fields': ('groups', 'user_permissions')}),
        ),)
    )

class GroupAdmin(ModelAdmin):
    model = auth.Group
    default_admin = True
    pages = (
        (None, (
            (None, {'fields': ('module_category', 'name')}),
        ),),
        (_('Permissions'), (
            (None, {'fields': ('permissions',)}),
        ),)
    )
