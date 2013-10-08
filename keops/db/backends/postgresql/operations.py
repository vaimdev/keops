from django.db.backends.postgresql_psycopg2 import operations as postgresql_psycopg2


def pg_lookup_cast(self, lookup_type):
    lookup = '%s'

    # Cast text lookups to text to allow things like filter(x__contains=4)
    if lookup_type in ('iexact', 'contains', 'icontains', 'startswith',
                       'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'):
        lookup = "UNACCENT(%s::text)"

    return lookup

postgresql_psycopg2.DatabaseOperations.lookup_cast = pg_lookup_cast
