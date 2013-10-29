from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.text import capfirst
from django.db.models.deletion import ProtectedError
from django.db import models, transaction
from django.contrib import messages
from django.contrib.admin.util import model_ngettext
from django.utils.encoding import force_text
from keops.http import HttpMessagesResponse


def delete_selected(modeladmin, request, queryset):
    from keops.db import get_db
    using = get_db(request)
    try:
        n = queryset.count()
        with transaction.atomic(using=using):
            for obj in queryset:
                obj.delete()
                modeladmin.log_deletion(request, obj, force_text(obj))
            modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
    except ProtectedError as e:
        modeladmin.message_user(request,
            _('Cannot delete the records because they are referenced through a protected foreign key!') +
            '<br>' + '<br>'.join([capfirst(str(obj.__class__._meta.verbose_name)) + ': ' + str(obj)
                                 for obj in e.protected_objects]), level=messages.ERROR, )
    except models.validators.ValidationError as e:
        modeladmin.message_user(request, '<br>'.join(e.messages), level=messages.ERROR)

    return HttpMessagesResponse(request._messages)

delete_selected.short_description = capfirst(ugettext_lazy('delete'))
delete_selected.category = ugettext_lazy('record')
delete_selected.attrs = 'ng-click="confirmDelete()"'


def duplicate_selected(modeladmin, request, queryset):
    return modeladmin.duplicate(request, queryset.all()[0])

duplicate_selected.short_description = capfirst(ugettext_lazy('duplicate'))
duplicate_selected.category = ugettext_lazy('record')
duplicate_selected.attrs = 'ng-click="form.newItem(form.item.pk)"'
