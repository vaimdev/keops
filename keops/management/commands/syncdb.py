
import os
from importlib import import_module
from optparse import make_option

from django.core.management import call_command
from django.core.management.commands import syncdb
from django.db import models

class Command(syncdb.Command):

    def handle_noargs(self, **options):
        db = options.get('database')
        verbosity = options.get('verbosity')

        # Bypass loaddata command on migrate/syncdb to load initial data only for installed apps
        load_initial_data = options.get('load_initial_data')
        options['load_initial_data'] = False
        apps = []
        def app_sync(sender, *args, **kwargs):
            created_models = kwargs.get('created_models')
            for model in created_models:
                mod_name = '.'.join(model.__module__.split('.')[:-1])
                if not mod_name in apps:
                    apps.append(mod_name)
        models.signals.post_syncdb.connect(app_sync)
        super(Command, self).handle_noargs(**options)
        models.signals.post_syncdb.disconnect(app_sync)
        
        # Load initial data from sync apps
        if load_initial_data:
            fixtures = []
            for app in apps:
                mod = import_module(app)
                dname = os.path.dirname(mod.__file__)
                fname = os.path.join(dname, 'fixtures', 'initial_data.json')
                if os.path.isfile(fname):
                    fixtures.append(fname)
                if hasattr(mod, 'app_info'):
                    fixtures += [os.path.join(dname, 'fixtures', f) for f in mod.app_info.get('fixtures', [])]

            if fixtures:
                if fname in fixtures:
                    call_command('loaddata', fname, verbosity=verbosity,
                                 database=db, skip_validation=False)
                    fixtures.remove(fname)
                if fixtures:
                    call_command('loadfixtures', *fixtures, verbosity=verbosity,
                                 database=db, skip_validation=False)
