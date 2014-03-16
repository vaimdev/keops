from __future__ import unicode_literals

from django.conf import settings
from django.db.backends import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = 'keops.db.backends.sqlserver.compiler'

    def __init__(self, connection):
        super(DatabaseOperations, self).__init__(connection)

    def date_extract_sql(self, lookup_type, field_name):
        if lookup_type == 'week_day':
            # For consistency across backends, we return Sunday=1, Saturday=7.
            return "datepart(dw, %s) + 1" % field_name
        else:
            return "datepart(%s, %s)" % (lookup_type, field_name)

    def date_interval_sql(self, sql, connector, timedelta):
        modifiers = []
        if timedelta.days:
            modifiers.append('%s days' % timedelta.days)
        if timedelta.seconds:
            modifiers.append('%s seconds' % timedelta.seconds)
        if timedelta.microseconds:
            modifiers.append('%s microseconds' % timedelta.microseconds)
        mods = ' '.join(modifiers)
        conn = ' %s ' % connector
        return '(%s)' % conn.join([sql, 'interval \'%s\'' % mods])

    def date_trunc_sql(self, lookup_type, field_name):
        return "cast(%s as %s)" % (field_name, lookup_type)

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        if lookup_type == 'week_day':
            # For consistency across backends, we return Sunday=1, Saturday=7.
            sql = "datepart(dw, %s) + 1" % field_name
        else:
            sql = "datepart(%s, %s)" % (lookup_type, field_name)
        return sql, params

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        params = []
        sql = "cast(%s as %s)" % (field_name, lookup_type)
        return sql, params

    def lookup_cast(self, lookup_type):
        return '%s'

    def field_cast_sql(self, db_type, internal_type):
        return '%s'

    def no_limit_value(self):
        return None

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return '"%s"' % name

    def prep_for_iexact_query(self, x):
        return x

    def max_name_length(self):
        return 128

    def distinct_sql(self, fields):
        if fields:
            return 'DISTINCT %s' % ', '.join(fields)
        else:
            return 'DISTINCT'

    def return_insert_id(self):
        return "OUTPUT inserted.%s", ()

    def bulk_insert_sql(self, fields, num_values):
        items_sql = "(%s)" % ", ".join(["%s"] * len(fields))
        return "VALUES " + ", ".join([items_sql] * num_values)

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        """
        Returns a list of SQL statements required to remove all data from
        the given database tables (without actually removing the tables
        themselves).

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.
        """
        if tables:
            # Cannot use TRUNCATE on tables that are referenced by a FOREIGN KEY
            # So must use the much slower DELETE
            from django.db import connections
            cursor = connections[self.connection.alias].cursor()
            # Try to minimize the risks of the braindeaded inconsistency in
            # DBCC CHEKIDENT(table, RESEED, n) behavior.
            seqs = []
            for seq in sequences:
                cursor.execute("SELECT COUNT(*) FROM %s" % self.quote_name(seq["table"]))
                rowcnt = cursor.fetchone()[0]
                elem = {}
                if rowcnt:
                    elem['start_id'] = 0
                else:
                    elem['start_id'] = 1
                elem.update(seq)
                seqs.append(elem)
            cursor.execute("SELECT TABLE_NAME, CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_TYPE not in ('PRIMARY KEY','UNIQUE')")
            fks = cursor.fetchall()
            sql_list = ['ALTER TABLE %s NOCHECK CONSTRAINT %s;' % \
                    (self.quote_name(fk[0]), self.quote_name(fk[1])) for fk in fks]
            sql_list.extend(['%s %s %s;' % (style.SQL_KEYWORD('DELETE'), style.SQL_KEYWORD('FROM'),
                             style.SQL_FIELD(self.quote_name(table)) ) for table in tables])

            # Then reset the counters on each table.
            sql_list.extend(['%s %s (%s, %s, %s) %s %s;' % (
                style.SQL_KEYWORD('DBCC'),
                style.SQL_KEYWORD('CHECKIDENT'),
                style.SQL_FIELD(self.quote_name(seq["table"])),
                style.SQL_KEYWORD('RESEED'),
                style.SQL_FIELD('%d' % seq['start_id']),
                style.SQL_KEYWORD('WITH'),
                style.SQL_KEYWORD('NO_INFOMSGS'),
                ) for seq in seqs])

            sql_list.extend(['ALTER TABLE %s CHECK CONSTRAINT %s;' % \
                    (self.quote_name(fk[0]), self.quote_name(fk[1])) for fk in fks])
            return sql_list
        else:
            return []
