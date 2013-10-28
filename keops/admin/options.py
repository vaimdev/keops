from django.contrib import admin


__all__ = ['modeladmin_factory', 'ModelAdmin']


def modeladmin_factory(cls, model):
    if cls:
        data = {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}
    else:
        data = {}
    return type('ModelAdmin_' + model._meta.app_label + '_' + model._meta.model_name.replace('.', '_'), (ModelAdmin,), data)


class ModelAdmin(admin.ModelAdmin):
    pass
