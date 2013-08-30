
from optparse import make_option

from django.core.management.base import AppCommand
from django.core.management.sql import sql_create
from django.db import connections, DEFAULT_DB_ALIAS
from django.conf import settings

class Command(AppCommand):
    help = "Install modules for the given app name(s)."

    option_list = AppCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to install the '
                'module. Defaults to the "default" database.'),
    )

    output_transaction = True

    def handle_app(self, app, **options):
        print('install app')
        from keops.db import scripts
        db = options['database']
        if scripts.install('.'.join(app.__name__.split('.')[:-1]), db):
            scripts.syncdb(db)
            print('Application "%s" successfully installed on database "%s".' % (app.__name__.split('.')[-2], db))
