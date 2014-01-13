from django.db.backends import BaseDatabaseIntrospection, FieldInfo
from django.utils.encoding import force_text
import pyodbc as Database

SQL_AUTOFIELD = -777555


class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Map type codes to Django Field types.
    data_types_reverse = {
        SQL_AUTOFIELD:                  'AutoField',
        Database.SQL_BIGINT:            'BigIntegerField',
        Database.SQL_BINARY:            'BinaryField',
        Database.SQL_BIT:               'BooleanField',
        Database.SQL_CHAR:              'CharField',
        Database.SQL_DECIMAL:           'DecimalField',
        Database.SQL_DOUBLE:            'FloatField',
        Database.SQL_FLOAT:             'FloatField',
        Database.SQL_GUID:              'TextField',
        Database.SQL_INTEGER:           'IntegerField',
        Database.SQL_LONGVARBINARY:     'BinaryField',
        Database.SQL_LONGVARCHAR:       'TextField',
        Database.SQL_NUMERIC:           'DecimalField',
        Database.SQL_REAL:              'FloatField',
        Database.SQL_SMALLINT:          'SmallIntegerField',
        Database.SQL_TINYINT:           'SmallIntegerField',
        Database.SQL_TYPE_DATE:         'DateField',
        Database.SQL_TYPE_TIME:         'TimeField',
        Database.SQL_TYPE_TIMESTAMP:    'DateTimeField',
        Database.SQL_VARBINARY:         'BinaryField',
        Database.SQL_VARCHAR:           'TextField',
        Database.SQL_WCHAR:             'CharField',
        Database.SQL_WLONGVARCHAR:      'TextField',
        Database.SQL_WVARCHAR:          'TextField',
    }

    def get_relations(self, cursor, table_name):
        return []

    def get_table_description(self, cursor, table_name):
        print(table_name, cursor)
        cursor.execute("""
            SELECT c.name, c.is_nullable FROM sys.tables t JOIN sys.columns c ON t.Object_ID = c.Object_ID
            WHERE t.name = ?""", [table_name])
        null_map = dict(cursor.fetchall())
        cursor.execute("SELECT * FROM %s WHERE 1 = 0" % self.connection.ops.quote_name(table_name))
        return [FieldInfo(*((force_text(line[0]),) + line[1:6] + (null_map[force_text(line[0])]==1,)))
                for line in cursor.description]

    def get_table_list(self, cursor):
        """
        Returns a list of table names in the current database.
        """
        cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        return [row[1] if row[0] == 'dbo' else row[0] + '.' + row[1] for row in cursor.fetchall()]
