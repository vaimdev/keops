
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Specifies the database to use. Default is "default".'),
    )

    def handle(self, *args, **options):
        from keops.db import scripts
        scripts.dropdb(options['database'])
        scripts.createdb(options['database'])
        scripts.syncdb(options['database'])
