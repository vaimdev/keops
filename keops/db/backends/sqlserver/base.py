"""
SQL Server database backend for Django.

Requires pyodbc
"""
import logging
import sys

from django.db.backends import *
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.safestring import SafeText, SafeBytes
from django.utils.timezone import utc

try:
    import pyodbc as Database
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading pyodbc module: %s" % e)

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class DatabaseFeatures(BaseDatabaseFeatures):
    can_return_id_from_insert = True


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

