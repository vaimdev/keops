import os
from importlib import import_module
from django.conf import settings

__all__ = ['register_modules']

def register_modules(prefix, path):
    lst = os.listdir(path)
    for s in lst:
        mod = '%s.%s' % (prefix, s)
        if os.path.isdir(os.path.join(path, s)) and not s.startswith(('_', '.')) and not mod in settings.INSTALLED_APPS:
            try:
                __import__(mod)
                settings.INSTALLED_APPS.append(mod)
            except:
                pass

    # adjust module dependency priority
    apps = settings.INSTALLED_APPS
    for app in apps:
        mod = import_module(app)
        info = getattr(mod, 'app_info', None)
        if info and 'dependencies' in info:
            apps.remove(app)
            deps = info.get('dependencies')
            i = 0
            for dep in deps:
                dep = dep.replace('-', '_')
                if not dep in apps:
                    apps.append(dep)
                    i = len(apps) - 1
                    continue
                i = max(i, apps.index(dep))
            if i == 0:
                apps.append(app)
            else:
                apps.insert(i + 1, app)

# Auto register modules on settings.INSTALLED_APPS
register_modules('keops.modules', os.path.dirname(__file__))
