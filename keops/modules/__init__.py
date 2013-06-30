
import os
import keops.settings

def register_modules(prefix, path):
    lst = os.listdir(path)
    for s in lst:
        if os.path.isdir(os.path.join(path, s)) and not s.startswith(('_', '.')):
            try:
                mod = '%s.%s' % (prefix, s)
                __import__(mod)
                keops.settings.INSTALLED_APPS.append(mod)
            except:
                pass

# Auto register modules on settings.INSTALLED_APPS
register_modules('keops.modules', os.path.dirname(__file__))
