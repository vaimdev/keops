from django.db.models.sql import compiler
from django.utils.six.moves import zip_longest


class SQLCompiler(compiler.SQLCompiler):
    def as_sql(self, with_limits=True, with_col_aliases=False):
        """
        Creates the SQL for this query. Returns the SQL string and list
        of parameters.  This is overriden from the original Query class
        to handle the additional SQL Oracle requires to emulate LIMIT
        and OFFSET.

        If 'with_limits' is False, any limit/offset information is not
        included in the query.
        """
        if with_limits and self.query.low_mark == self.query.high_mark:
            return '', ()

        sql, params = super(SQLCompiler, self).as_sql(False, with_col_aliases)

        if with_limits:
            ordering, o_params, ordering_group_by = self.get_ordering()
            if not ordering:
                sql += """ ORDER BY 1 """
            if self.query.high_mark is None and not self.query.low_mark is None:
                sql += """ OFFSET %d ROWS FETCH NEXT 1 ROWS ONLY""" % self.query.low_mark
            else:
                sql += """ OFFSET %d ROWS FETCH NEXT %d ROWS ONLY""" % (self.query.low_mark, self.query.high_mark)
        return sql, params


class SQLInsertCompiler(compiler.SQLInsertCompiler):
    def as_sql(self):
        # We don't need quote_name_unless_alias() here, since these are all
        # going to be column names (so we can avoid the extra overhead).
        qn = self.connection.ops.quote_name
        opts = self.query.get_meta()
        fields = self.query.fields
        table_name = qn(opts.db_table)
        result = []
        if opts.has_auto_field and opts.auto_field.column in [f.column for f in fields]:
            identity_insert = 'SET IDENTITY_INSERT %s OFF;' % table_name
            result.append('SET IDENTITY_INSERT %s ON;' % table_name)
        else:
            identity_insert = ''
        result.append('INSERT INTO %s' % table_name)

        has_fields = bool(self.query.fields)
        if not has_fields:
            result.append('OUTPUT inserted.* DEFAULT VALUES')
            return [(' '.join(result), ())]
        result.append('(%s)' % ', '.join([qn(f.column) for f in fields]))

        if has_fields:
            params = values = [
                [
                    f.get_db_prep_save(getattr(obj, f.attname) if self.query.raw else f.pre_save(obj, True), connection=self.connection)
                    for f in fields
                ]
                for obj in self.query.objs
            ]
        else:
            values = [[self.connection.ops.pk_default_value()] for obj in self.query.objs]
            params = [[]]
            fields = [None]
        can_bulk = (not any(hasattr(field, "get_placeholder") for field in fields) and
            not self.return_id and self.connection.features.has_bulk_insert)

        if can_bulk:
            placeholders = [["%s"] * len(fields)]
        else:
            placeholders = [
                [self.placeholder(field, v) for field, v in zip(fields, val)]
                for val in values
            ]
            # Oracle Spatial needs to remove some values due to #10888
            params = self.connection.ops.modify_insert_params(placeholders, params)
        if self.return_id and self.connection.features.can_return_id_from_insert:
            params = params[0]
            col = qn(opts.pk.column)
            r_fmt, r_params = self.connection.ops.return_insert_id()
            # Skip empty r_fmt to allow subclasses to customize behaviour for
            # 3rd party backends. Refs #19096.
            if r_fmt:
                print(r_fmt, col)
                result.append(r_fmt % col)
                params += r_params
            result.append("VALUES (%s);" % ", ".join(placeholders[0]))
            result.append(identity_insert)
            return [(" ".join(result), tuple(params))]
        if can_bulk:
            result.append(self.connection.ops.bulk_insert_sql(fields, len(values)))
            return [(" ".join(result), tuple([v for val in values for v in val]))]
        else:
            return [
                (" ".join(result + ["VALUES (%s);%s" % (", ".join(p), identity_insert)]), vals)
                for p, vals in zip(placeholders, params)
            ]

class SQLDeleteCompiler(compiler.SQLDeleteCompiler):
    pass

class SQLUpdateCompiler(compiler.SQLUpdateCompiler):
    pass

class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    pass

class SQLDateCompiler(compiler.SQLDateCompiler):
    pass

class SQLDateTimeCompiler(compiler.SQLDateTimeCompiler):
    pass
