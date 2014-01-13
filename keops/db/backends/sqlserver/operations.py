from __future__ import unicode_literals

from django.conf import settings
from django.db.backends import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
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
        return "OUTPUT inserted.*", ()

    def bulk_insert_sql(self, fields, num_values):
        items_sql = "(%s)" % ", ".join(["%s"] * len(fields))
        return "VALUES " + ", ".join([items_sql] * num_values)
