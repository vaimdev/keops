
from django.utils.translation import ugettext_lazy as _
from keops.forms.admin import ModelAdmin
from keops.modules.base import auth

class UserAdmin(ModelAdmin):
    model = auth.User
    admin_default = True
    pages = (
        (None, (
            (None, {'fields': ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',)}),
        ),),
        (_('Permissions'), (
            (None, {'fields': ('groups', 'user_permissions')}),
        ),)
    )

class GroupAdmin(ModelAdmin):
    model = auth.Group
    admin_default = True
    pages = (
        (None, (
            (None, {'fields': ('name',)}),
        ),),
        (_('Permissions'), (
            (None, {'fields': ('permissions',)}),
        ),)
    )
