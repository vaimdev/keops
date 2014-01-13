import os
import sys

from django.db.backends import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'osql'

    def runshell(self):
        settings_dict = self.connection.settings_dict
        user = settings_dict['OPTIONS'].get('user', settings_dict['USER'])
        password = settings_dict['OPTIONS'].get('passwd', settings_dict['PASSWORD'])
        db = settings_dict['OPTIONS'].get('db', settings_dict['NAME'])
        server = settings_dict['OPTIONS'].get('host', settings_dict['HOST'])
        port = settings_dict['OPTIONS'].get('port', settings_dict['PORT'])
        defaults_file = settings_dict['OPTIONS'].get('read_default_file')

        args = [self.executable_name]
        if server:
            args += ["-S", server]
        if user:
            args += ["-U", user]
            if password:
                args += ["-P", password]
        else:
            args += ["-E"]  # Try trusted connection instead
        if db:
            args += ["-d", db]
        if defaults_file:
            args += ["-i", defaults_file]

        sys.exit(os.system(" ".join(args)))
