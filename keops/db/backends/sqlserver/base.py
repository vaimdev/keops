"""
SQL Server 2005+ Native database backend for Django.

Requires pyodbc for now (soon pysqlncli)
"""
import logging
import sys
import os

from django.db.backends import *
from keops.db.backends.sqlserver.operations import DatabaseOperations
from keops.db.backends.sqlserver.client import DatabaseClient
from keops.db.backends.sqlserver.creation import DatabaseCreation
from keops.db.backends.sqlserver.introspection import DatabaseIntrospection
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.safestring import SafeText, SafeBytes
from django.utils.timezone import utc
from keops.db.backends.sqlserver import util

try:
    import pyodbc as Database
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading pyodbc module: %s" % e)

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class DatabaseFeatures(BaseDatabaseFeatures):
    can_return_id_from_insert = True
    supports_transactions = True


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'sqlserver'
    operators = {
        'exact': '= %s',
        'iexact': '= %s',
        'contains': "LIKE %s ESCAPE '\\'",
        'icontains': "LIKE %s ESCAPE '\\'",
        'regex': 'LIKE %s',
        'iregex': 'LIKE %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': "LIKE %s ESCAPE '\\'",
        'endswith': "LIKE %s ESCAPE '\\'",
        'istartswith': "LIKE %s ESCAPE '\\'",
        'iendswith': "LIKE %s ESCAPE '\\'",
    }

    Database = Database

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        opts = self.settings_dict["OPTIONS"]
        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)

    def get_connection_params(self):
        """Returns a dict of parameters suitable for get_new_connection."""
        settings_dict = self.settings_dict
        conn_params = {
            'database': settings_dict['NAME'],
        }
        conn_params.update(settings_dict['OPTIONS'])
        if 'autocommit' in conn_params:
            del conn_params['autocommit']
        if 'isolation_level' in conn_params:
            del conn_params['isolation_level']
        if settings_dict['USER']:
            conn_params['user'] = settings_dict['USER']
        if settings_dict['PASSWORD']:
            conn_params['password'] = force_str(settings_dict['PASSWORD'])
        if settings_dict['HOST']:
            conn_params['host'] = settings_dict['HOST']
        if settings_dict['PORT']:
            conn_params['port'] = settings_dict['PORT']
        conn_params.setdefault('driver', 'SQL Server')
        return conn_params

    def init_connection_state(self):
        pass

    def create_cursor(self):
        return self.connection.cursor()

    def get_new_connection(self, conn_params):
        """Opens a connection to the database."""
        conn_params = self.get_connection_params()
        autocommit = conn_params.get('autocommit', True)
        if 'connection_string' in conn_params:
            return Database.connect(conn_params, autocommit=autocommit)
        conn = []
        if 'dsn' in conn_params:
            conn.append('DSN=%s' % conn_params['dsn'])
        else:
            driver = conn_params['driver']
            if os.path.isabs(driver):
                conn.append('DRIVER=%s' % driver)
            else:
                conn.append('DRIVER={%s}' % driver)

        conn.append('SERVER=%s' % conn_params['host'])
        if 'port'in conn_params:
            conn.append('PORT=%s' % conn_params['port'])
        if conn_params['database']:
            conn.append('DATABASE=%s' % conn_params['database'])
        if conn_params['user']:
            conn.append('UID=%s;PWD=%s' % (conn_params['user'], conn_params['password']))
        else:
            conn.append('Integrated Security=SSPI')
        return Database.connect(';'.join(conn), autocommit=autocommit, unicode_results=True)

    def make_debug_cursor(self, cursor):
        """
        Creates a cursor that logs all queries in self.queries.
        """
        return util.CursorDebugWrapper(cursor, self)

    def cursor(self):
        """
        Creates a cursor, opening a connection if necessary.
        """
        self.validate_thread_sharing()
        if (self.use_debug_cursor or
            (self.use_debug_cursor is None and settings.DEBUG)):
            cursor = self.make_debug_cursor(self._cursor())
        else:
            cursor = util.CursorWrapper(self._cursor(), self)
        return cursor

    def _set_autocommit(self, autocommit):
        """
        Backend-specific implementation to enable or disable autocommit.
        """
        pass
