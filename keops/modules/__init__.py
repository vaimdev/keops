import os
from importlib import import_module
from django.conf import settings

__all__ = ['register_modules', 'adjust_dependencies']


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
    adjust_dependencies(settings.INSTALLED_APPS)


def get_dependencies(app):
    r = []
    mod = import_module(app)
    info = getattr(mod, 'app_info', None)
    if info and 'dependencies' in info:
        deps = [d.replace('-', '_') for d in list(info.get('dependencies'))]
        for dep in deps:
            r += get_dependencies(dep)
        return r + deps
    return []


def adjust_dependencies(apps):
    # adjust module dependency priority

    for app in apps:
        deps = get_dependencies(app)
        if deps:
            apps.remove(app)
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

# Adjust modules dependencies
adjust_dependencies(settings.INSTALLED_APPS)
# TODO: Enable multiple database support
