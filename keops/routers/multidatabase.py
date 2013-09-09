# Enable django to work with multi database using DATABASE_ROUTER settings

import copy

class MultiDatabaseRouter(object):
    APPS_CACHE = {}

    def _get_connection_apps(self, db):
        apps = self.APPS_CACHE.get(db, [])
        if not apps:
            from keops import settings
            apps = [s.split('.')[-1] for s in settings.INSTALLED_APPS]
            try:
                # cache all installed modules
                from keops.modules.base import models
                apps.extend([r.app_label for r in models.Module.objects.using(db).all()])
            except:
                pass
        return apps

    def db_for_read(self, model, **hints):
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_syncdb(self, db, model):
        apps = self._get_connection_apps(db)
        return model._meta.app_label in apps
