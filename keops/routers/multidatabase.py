# Enable keops to work with multi database using DATABASE_ROUTER settings
# each db have your own installed apps (registered on base.module)
# by default keops installs all apps defined on BASE_APPS settings
from keops.middleware.threadlocal import get_db

class MultiDatabaseRouter(object):
    _app_cache = {}

    def _get_connection_apps(self, db):
        apps = self._app_cache.get(db, [])
        if not apps:
            from keops import settings
            from keops.modules import adjust_dependencies

            # Adjust BASE_APPS dependencies
            adjust_dependencies(settings.BASE_APPS)
            apps = [s.split('.')[-1] for s in settings.BASE_APPS]
            try:
                # cache all installed modules
                from keops.modules.base import models
                apps.extend([ r.app_label for r in models.Module.objects.using(db).all() ])
            except:
                pass
            self._app_cache[db] = apps
        return apps

    def db_for_read(self, model, **hints):
        return get_db()
    
    def db_for_write(self, model, **hints):
        return get_db()
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_syncdb(self, db, model):
        apps = self._get_connection_apps(db)
        return model._meta.app_label in apps
