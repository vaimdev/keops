from django.db import models
from django.db.backends.util import truncate_name
from django.db.backends.postgresql_psycopg2 import creation as postgresql_psycopg2

# Optimize postgres char db field indexes
def pg_sql_indexes_for_field(self, model, f, style):
    output = []
    if f.db_index or f.unique:
        db_type = f.db_type(connection=self.connection)

        def SQL_FIELD():
            name = style.SQL_FIELD(qn(f.column))
            if db_type.startswith('varchar'):
                if isinstance(f, models.CharField):
                    name = 'unaccent(%s)' % name
            return name

        qn = self.connection.ops.quote_name
        db_table = model._meta.db_table
        tablespace = f.db_tablespace or model._meta.db_tablespace
        if tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(tablespace)
            if tablespace_sql:
                tablespace_sql = ' ' + tablespace_sql
        else:
            tablespace_sql = ''

        def get_index_sql(index_name, opclass='', using=''):
            return (style.SQL_KEYWORD('CREATE INDEX') + ' ' +
                    style.SQL_TABLE(qn(truncate_name(index_name,self.connection.ops.max_name_length()))) + ' ' +
                    style.SQL_KEYWORD('ON') + ' ' +
                    style.SQL_TABLE(qn(db_table)) + ' ' + using + ' ' +
                    "(%s%s)" % (SQL_FIELD(), opclass) +
                    "%s;" % tablespace_sql)

        # Fields with database column types of `varchar` and `text` need
        # a second index that specifies their operator class, which is
        # needed when performing correct LIKE queries outside the
        # C locale. See #12234.
        if not f.unique:
            output = [get_index_sql('%s_%s' % (db_table, f.column))]

        if db_type.startswith('varchar'):
            output.append(get_index_sql('%s_%s_like' % (db_table, f.column),
                                        ' gist_trgm_ops', 'USING gist'))
        elif db_type.startswith('text'):
            output.append(get_index_sql('%s_%s_like' % (db_table, f.column),
                                        ' text_pattern_ops'))
    return output

postgresql_psycopg2.DatabaseCreation.sql_indexes_for_field = pg_sql_indexes_for_field
