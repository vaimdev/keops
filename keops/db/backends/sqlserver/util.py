from django.db.backends import util


class CursorWrapper(util.CursorWrapper):
    def execute(self, sql, params=None):
        sql = sql.replace('%s', '?')
        print('sql', sql, params)
        return super(CursorWrapper, self).execute(sql, params)


class CursorDebugWrapper(util.CursorDebugWrapper):
    def execute(self, sql, params=None):
        sql = sql.replace('%s', '?')
        print('sql', sql, params)
        return super(CursorDebugWrapper, self).execute(sql, params)
