from django.db.backends.creation import BaseDatabaseCreation
from django.db.backends.util import truncate_name


class DatabaseCreation(BaseDatabaseCreation):
    data_types = {
        'AutoField':         'int identity(1,1)',
        'BinaryField':       'binary',
        'BooleanField':      'bit',
        'CharField':         'nvarchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'nvarchar(%(max_length)s)',
        'DateField':         'datetime',
        'DateTimeField':     'datetime',
        'DecimalField':      'numeric(%(max_digits)s, %(decimal_places)s)',
        'FileField':         'nvarchar(%(max_length)s)',
        'FilePathField':     'nvarchar(%(max_length)s)',
        'FloatField':        'double precision',
        'IntegerField':      'int',
        'BigIntegerField':   'bigint',
        'IPAddressField':    'char(15)',
        'GenericIPAddressField': 'char(39)',
        'NullBooleanField':  'bit',
        'OneToOneField':     'int',
        'PositiveIntegerField': 'int',
        'PositiveSmallIntegerField': 'smallint',
        'SlugField':         'nvarchar(%(max_length)s)',
        'SmallIntegerField': 'smallint',
        'TextField':         'text',
        'TimeField':         'time',
    }

    def _destroy_test_db(self, test_database_name, verbosity):
        """
        Internal implementation - remove the test db tables.
        """
        # Remove the test database to clean up after
        # ourselves. Connect to the previous database (not the test database)
        # to do so, because it's not allowed to delete a database while being
        # connected to it.
        cursor = self.connection.cursor()
        # Wait to avoid "database is being accessed by other users" errors.
        cursor.execute('ALTER DATABASE %s SET SINGLE_USER WITH ROLLBACK IMMEDIATE;' % self.connection.ops.quote_name(test_database_name))
        cursor.execute("DROP DATABASE %s"
                       % self.connection.ops.quote_name(test_database_name))
        self.connection.close()

    def _prepare_for_test_db_ddl(self):
        self.connection.connection.rollback()
        self.connection.connection.autocommit = True

