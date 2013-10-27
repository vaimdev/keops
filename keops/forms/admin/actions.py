from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.db.models.deletion import ProtectedError
from django.db import models
from keops.http import HttpJsonResponse


def delete_selected(modeladmin, request, queryset):
    from keops.db import get_db
    using = get_db(request)
    for obj in queryset:
        try:
            modeladmin.delete(request, obj, using=using)
        except ProtectedError as e:
            return HttpJsonResponse({
                'success': False,
                'action': 'DELETE',
                'label': _('Error'),
                'msg': _('Cannot delete the records because they are referenced through a protected foreign key!') +
                        '<br>' + '<br>'.join([capfirst(str(obj.__class__._meta.verbose_name)) + ': ' + str(obj)
                                             for obj in e.protected_objects]),
            })
        except models.validators.ValidationError as e:
            return HttpJsonResponse({
                'success': False,
                'action': 'DELETE',
                'label': _('Error'),
                'msg': '<br>'.join(e.messages),
            })

        return HttpJsonResponse({
            'success': True,
            'action': 'DELETE',
            'label': _('Success'),
            'msg': _('Record successfully deleted!'),
        })

delete_selected.short_description = capfirst(_('delete'))


def duplicate_selected(modeladmin, request, queryset):
    modeladmin.duplicate(request, queryset)

duplicate_selected.short_description = capfirst(_('duplicate'))
