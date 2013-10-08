
from django.db import models
from django.db.backends import creation
from django.db.backends.util import truncate_name
from django.db.backends.postgresql_psycopg2 import creation as postgresql_psycopg2

# Monkey patch base database creation class, to improve create model proxy additional fields
class BaseDatabaseCreation(object):
    _sql_create_model = creation.BaseDatabaseCreation.sql_create_model

    def sql_create_model(self, model, style, known_models=set()):
        """
        Returns the SQL required to create a single model, as a tuple of:
            (list_of_sql, pending_references_dict)
        """
        opts = model._meta
        if not opts.proxy:
            return BaseDatabaseCreation._sql_create_model(self, model, style, known_models)
        elif not opts.managed or (opts.proxy and not opts.local_fields) or opts.swapped:
            return [], {}

        table_output = []
        pending_references = {}
        qn = self.connection.ops.quote_name
        for f in opts.local_fields:
            col_type = f.db_type(connection=self.connection)
            tablespace = f.db_tablespace or opts.db_tablespace
            if col_type is None:
                # Skip ManyToManyFields, because they're not represented as
                # database columns in this table.
                continue
            # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
            field_output = [style.SQL_FIELD(qn(f.column)),
                style.SQL_COLTYPE(col_type)]
            # Oracle treats the empty string ('') as null, so coerce the null
            # option whenever '' is a possible value.
            null = f.null
            if (f.empty_strings_allowed and not f.primary_key and
                    self.connection.features.interprets_empty_strings_as_nulls):
                null = True
            if not null:
                field_output.append(style.SQL_KEYWORD('NOT NULL'))
            if f.primary_key:
                field_output.append(style.SQL_KEYWORD('PRIMARY KEY'))
            elif f.unique:
                field_output.append(style.SQL_KEYWORD('UNIQUE'))
            if tablespace and f.unique:
                # We must specify the index tablespace inline, because we
                # won't be generating a CREATE INDEX statement for this field.
                tablespace_sql = self.connection.ops.tablespace_sql(
                    tablespace, inline=True)
                if tablespace_sql:
                    field_output.append(tablespace_sql)
            if f.rel and f.db_constraint:
                ref_output, pending = self.sql_for_inline_foreign_key_references(
                    model, f, known_models, style)
                if pending:
                    pending_references.setdefault(f.rel.to, []).append(
                        (model, f))
                else:
                    field_output.extend(ref_output)
            table_output.append(' '.join(field_output))
        for field_constraints in opts.unique_together:
            table_output.append(style.SQL_KEYWORD('UNIQUE') + ' (%s)' %
                ", ".join(
                    [style.SQL_FIELD(qn(opts.get_field(f).column))
                     for f in field_constraints]))

        full_statement = []

        for i, line in enumerate(table_output):  # Combine and add commas.
            full_statement.append(style.SQL_KEYWORD('ALTER TABLE') + ' ' +
                                  style.SQL_TABLE(qn(opts.db_table)) + ' ' +
                                  '    ADD %s;' % line)
        if opts.db_tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(
                opts.db_tablespace)
            if tablespace_sql:
                full_statement.append(tablespace_sql)
        #full_statement.append(';')
        final_output = full_statement

        if opts.has_auto_field:
            # Add any extra SQL needed to support auto-incrementing primary
            # keys.
            auto_column = opts.auto_field.db_column or opts.auto_field.name
            autoinc_sql = self.connection.ops.autoinc_sql(opts.db_table,
                                                          auto_column)
            if autoinc_sql:
                for stmt in autoinc_sql:
                    final_output.append(stmt)
        return final_output, pending_references

    # Monkey-patch (adjust on delete cascade to database relations)
    def sql_for_pending_references(self, model, style, pending_references):
        """
        Returns any ALTER TABLE statements to add constraints after the fact.
        """
        opts = model._meta
        if not opts.managed or opts.proxy or opts.swapped:
            return []
        qn = self.connection.ops.quote_name
        final_output = []
        if model in pending_references:
            for rel_class, f in pending_references[model]:
                rel_opts = rel_class._meta
                r_table = rel_opts.db_table
                r_col = f.column
                table = opts.db_table
                col = opts.get_field(f.rel.field_name).column
                # For MySQL, r_name must be unique in the first 64 characters.
                # So we are careful with character usage here.
                r_name = '%s_refs_%s_%s' % (
                    r_col, col, self._digest(r_table, table))
                print('relation', r_name)
                if f.rel.on_delete == models.CASCADE:
                    cascade = ' ON DELETE CASCADE '
                else:
                    cascade = ''
                print(f, cascade)
                final_output.append(style.SQL_KEYWORD('ALTER TABLE') +
                    ' %s ADD CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s (%s)%s%s;' %
                    (qn(r_table), qn(truncate_name(
                        r_name, self.connection.ops.max_name_length())),
                    qn(r_col), qn(table), qn(col),
                    cascade,
                    self.connection.ops.deferrable_sql()))
            del pending_references[model]
        return final_output

    creation.BaseDatabaseCreation.sql_create_model = sql_create_model
    creation.BaseDatabaseCreation.sql_for_pending_references = sql_for_pending_references


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
