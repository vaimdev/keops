import os
from importlib import import_module
from django.conf import settings
from django.apps import apps as django_apps
from keops.apps import AppConfig

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
    if isinstance(app, str):
        app = AppConfig.create(app)
    deps = getattr(app, 'dependencies', None)
    if deps:
        for dep in app.dependencies:
            r += get_dependencies(dep)
        return r + app.dependencies
    return []


def adjust_dependencies(apps):
    # adjust module dependency priority
    apps = list(apps)
    for entry in apps:
        deps = get_dependencies(entry)
        if deps:
            apps.remove(entry)
            i = 0
            for dep in deps:
                if not dep in apps:
                    apps.append(dep)
                    i = len(apps) - 1
                    continue
                i = max(i, apps.index(dep))
            if i == 0:
                apps.append(entry)
            else:
                apps.insert(i + 1, entry)
    return apps


def populate(populate_fn):
    def inner(*args, **kwargs):
        if len(args) > 0:
            installed_apps = args[0]
        elif 'installed_apps' in kwargs:
            installed_apps = kwargs.get('installed_apps')
        kwargs['installed_apps'] = adjust_dependencies(installed_apps)
        populate_fn(**kwargs)
    return inner

# Patch django apps populate to adjust module dependency priority
django_apps.populate = populate(django_apps.populate)
