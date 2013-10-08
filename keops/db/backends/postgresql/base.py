from django.db.backends.postgresql_psycopg2.base import *

DatabaseWrapper.operators.update(
    {
        'exact': '= %s',
        'iexact': '= UPPER(UNACCENT(%s))',
        'contains': 'LIKE %s',
        'icontains': 'ILIKE UNACCENT(%s)',
        'regex': '~ %s',
        'iregex': '~* %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'ILIKE UNACCENT(%s)',
        'iendswith': 'ILIKE UNACCENT(%s)',
    }
)
