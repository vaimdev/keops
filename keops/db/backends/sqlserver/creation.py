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
