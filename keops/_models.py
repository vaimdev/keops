from django.db import models
from django.db.models import options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('Admin',)
import keops.db.base
import keops.db.fields



# Add data dict object to django model admin
class ModelAdmin(object):
    model = None
    default_fields = None
    status_field = None
    reports = None
    readonly = False
    after_insert = None
    after_update = None
    after_delete = None
    after_save = None
    after_change = None
    before_insert = None
    before_update = None
    before_delete = None
    before_save = None
    before_change = None
    field_groups = None
    _model_admin = None

    def __init__(self):
        if not self.field_groups:
            self.field_groups = {
                'display_fields': None,
                'editable_fields': None,
                'print_fields': None,
                'list_fields': None,
                'list_editable': None,
                'search_fields': None,
                'filter_fields': None,
            }
        # Auto detect display_expression
        if self.default_fields is None:
            fk = None
            for f in self.model._meta.fields:
                if isinstance(f, models.CharField):
                    self.default_fields = (f.name,)
                    break
                if isinstance(f, models.ForeignKey) and not fk:
                    fk = (f.name,)
            self.default_fields = self.default_fields or fk

        if not self.field_groups.get('list_fields'):
            self.field_groups['list_fields'] = [
                f.name for f in self.model._meta.fields
                if not isinstance(f, (models.AutoField, models.ManyToManyField)) and
                getattr(f, 'custom_attrs', {}).get('visible', not f.primary_key)]

        if not self.field_groups.get('search_fields'):
            self.field_groups['search_fields'] = self.default_fields

        # Auto detect status_field
        if self.status_field is None:
            try:
                f = self.model._meta.get_field('status')
                if f.choices:
                    self.state_field = 'status'
            except:
                pass

    @property
    def model_admin(self):
        if not self._model_admin:
            from keops.admin import modeladmin_factory, site
            self._model_admin = modeladmin_factory(self.model)(self.model, site)
            self._model_admin.extra = self
        return self._model_admin


def get_admin(self):
    if not self._admin:
        self._admin = self.Admin()
    return self._admin


options.Options.admin = property(get_admin)


def class_prepared(sender, *args, **kwargs):
    d = {'model': sender}
    if hasattr(sender._meta, 'Admin') and not issubclass(sender._meta.Admin, ModelAdmin):
        d.update(sender._meta.Admin.__dict__)
        del sender._meta.Admin
    if not hasattr(sender._meta, 'Admin'):
        admin = ModelAdmin
        for b in sender.__bases__:
            if hasattr(b, '_meta') and hasattr(b._meta, 'Admin'):
                admin = b._meta.Admin
                break
        sender._meta.Admin = type(sender.__name__ + 'Admin', (admin,), d)
    sender._meta._admin = None


models.signals.class_prepared.connect(class_prepared)

