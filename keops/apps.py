from django import apps


class AppConfig(apps.AppConfig):
    author = None
    category = None
    description = None
    dependencies = None
    fixtures = None
    demo_data = None
    installable = False
    sql = None
    version = None
    website = None


class SimpleConfig(apps.AppConfig):
    name = 'keops'


class AdminConfig(SimpleConfig):
    def ready(self):
        # auto-discover admin modules
        from django.contrib.admin import autodiscover_modules
        from keops.admin import site
        autodiscover_modules('admin', register_to=site)

        # search by model classes with Admin sub-class
        from django.apps import apps
        for app_config in apps.get_app_configs():
            for model in app_config.models.values():
                if hasattr(model._meta, 'Admin') and getattr(model._meta.Admin, 'admin_visible', True):
                    site.register(model)
