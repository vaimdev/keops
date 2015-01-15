import sys
import os
from optparse import make_option
from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from keops.db import scripts
from keops.apps import AppConfig


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS, help='Specifies the database to use. Default is "default".'),
    )
    help = 'Install database apps.'

    def handle(self, *args, **options):
        db = options['database']
        verbosity = options['verbosity']
        fixtures = []
        sqls = []
        for app in apps.app_configs:
            app = apps.app_configs[app]
            if isinstance(app, AppConfig):
                if app.fixtures:
                    for fixture in app.fixtures:
                        fixtures.append(os.path.join(app.path, 'fixtures', fixture))
                if app.sql:
                    for sql in app.sql:
                        sqls.append(os.path.join(app.path, 'sql', sql))
        if fixtures:
            call_command('loaddata', *fixtures, verbosity=verbosity, database=db, skip_validation=False)
        if sqls:
            for sql in sqls:
                try:
                    scripts.runfile(sql, db)
                except Exception as e:
                    sys.stderr.write('Couldn\'t execute "%s" SQL file.' % sql)
                    import traceback
                    traceback.print_exc()
