
import os
from importlib import import_module
from django.db import connections
from django.db.utils import load_backend

def _create_connection(database):
    connection = connections[database]
    db_settings = connection.settings_dict
    db_engine = db_settings['ENGINE']
    backend = load_backend(db_engine)
    db_engine = db_engine.split('.')[-1]

    if db_engine == 'sqlite3':
        import sqlite3
        return sqlite3.connect(db_settings['NAME'])
    elif db_engine.startswith('postgres'):
        return backend.psycopg2.connect("host='%s'  dbname='postgres' user='%s' password='%s'" %
            (db_settings['HOST'], db_settings['USER'], db_settings['PASSWORD']))
    elif db_engine == 'pyodbc':
        return backend.Database.connect("DRIVER={SQL Server Native Client 11.0};DATABASE=master;Server=%s;UID=%s;PWD=%s" % 
            (db_settings['HOST'], db_settings['USER'], db_settings['PASSWORD']))
    elif db_engine == 'oracle':
        import cx_Oracle
        conn = cx_Oracle.connect('SYSTEM', db_settings['PASSWORD'], 'localhost/master')
        return conn
    
def createdb(database):
    connection = connections[database]
    db_settings = connection.settings_dict
    db_engine = db_settings['ENGINE']
    db_name = db_settings['NAME']
    db_engine = db_engine.split('.')[-1]

    conn = _create_connection(database)
    print('Creating db "%s"' % db_name)

    if db_engine == 'sqlite3':
        pass
    elif db_engine.startswith('postgresql'):
        conn.autocommit = True
        conn.cursor().execute('''CREATE DATABASE %s ENCODING='UTF-8' ''' % db_name)
    elif db_engine == 'pyodbc':
        conn.autocommit = True
        conn.cursor().execute('''CREATE DATABASE %s''' % db_name)
        conn.autocommit = False
    elif db_engine == 'oracle':
        conn.cursor().execute('create user %s identified by %s' % (db_settings['USER'], db_settings['PASSWORD']))
        conn.cursor().execute('grant all privilege to %s' % db_settings['USER'])


def dropdb(database):
    connection = connections[database]
    connection.close()
    db_settings = connection.settings_dict
    db_engine = db_settings['ENGINE']
    db_name = db_settings['NAME']
    db_engine = db_engine.split('.')[-1]

    conn = _create_connection(database)
    print('Dropping db "%s"' % db_name)

    if db_engine == 'sqlite3':
        del conn
        os.remove(db_name)
    elif db_engine.startswith('postgres'):
        conn.autocommit = True
        try:
            conn.cursor().execute('''DROP DATABASE %s''' % db_name)
        except Exception as e:
            print(e)
        conn.autocommit = False
    elif db_engine == 'pyodbc':
        conn.autocommit = True
        try:
            conn.cursor().execute('''DROP DATABASE %s''' % db_name)
        except Exception as e:
            print(e)
        conn.autocommit = False
    elif db_engine == 'oracle':
        try:
            conn.cursor().execute('DROP USER %s CASCADE'% db_settings['USER'])
        except Exception as e:
            print(e)

def syncdb(database):
    from django.core.management import call_command
    call_command('syncdb', database=database, interactive=False)
    from django.conf import settings
    from django.utils import translation
    translation.activate(settings.LANGUAGE_CODE)

def recreatedb(database):
    dropdb(database)
    createdb(database)

def runfile(filename, database):
    f = open(filename, encoding='utf-8')
    conn = connections[database]
    conn.cursor().execute(f.read())


def install(app_name, database, demo=True):
    app_label = app_name.split('.')[-1]
    
    def install_app():
        try:
            app = import_module(app_name)
            path = os.path.dirname(app.__file__)
            if hasattr(app, 'app_info'):
                info = app.app_info
            else:
                info = { 'name': app.__name__, 'description': '', 'version': '0.1' }
            from keops.modules.base import models as base
            if base.Module.objects.using(database).filter(app_label=app_label):
                print('Application "%s" already installed on database "%s".' % (app_label, database))
                return
            else:
                base.Module.objects.using(database).create(
                    app_label=app_label,
                    name=app_name,
                    description=info['description'],
                    version=info.get('version', None),
                    dependencies=info.get('dependencies'),
                    icon=info.get('icon'),
                    visible=info.get('visible'),
                    tooltip=info.get('tooltip', ''),
                    db_version=info.get('db_version', 0)
                )
                return True
            # Auto register models
            if os.path.isfile(os.path.join(path, 'models.py')) or\
                os.path.isfile(os.path.join(path, 'models.pyc')):
                try:
                    pass
                    #models = import_module(app_name + '.models')
                    #base.BaseModel.register_models(models, module_id=mod.pk)
                    #importer.load_fixtures(models, info.get('fixtures', []), mod.pk)
                    #if demo:
                    #    importer.load_files(models, info.get('files', []), info.get('demo', []), mod.pk)
                except Exception as e:
                    raise
            #if os.path.isfile(os.path.join(path, 'install.py')) or\
            #    os.path.isfile(os.path.join(path, 'install.pyc')):
            #    install = import_module(app_name + '.install')
            #    if hasattr(install, 'install'):
            #        install.install()
            #    if demo and hasattr(install, 'demo'):
            #        install.demo()
        except Exception as e:
            raise
            import traceback
            print(e)
            traceback.print_exc()

    from django.conf import settings
    return install_app()
