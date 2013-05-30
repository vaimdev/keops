# Enable orun to work with multi database using DATABASE_ROUTER setting

class MultiDatabaseRouter(object):
    def db_for_read(self, model, **hints):
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_syncdb(self, db, model):
        # Basic apps
        apps = ('sessions', 'sites', 'contenttypes', 'auth', 'base', 'admin')
        app_label = model._meta.app_label
        try:
            from keops.modules.base import models
            apps.extend([r.app_label for r in models.Module.objects.using(db).all()])
        except:
            pass
        return app_label in apps
