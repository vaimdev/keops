DEBUG = True

SITE_ID = 1
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'
TEMPLATE_DIRS = []

DATABASE_ROUTERS = ['keops.routers.multidatabase.MultiDatabaseRouter']
DATABASES = {'default': {}}

AUTH_USER_MODEL = 'base.user'

INSTALLED_APPS = [
    'keops',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.messages',
    'keops.modules.base',
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware', TODO: implement csrf on extjs
    'keops.middleware.threadlocal.ThreadLocalMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# IMPORTANT! MULTI-DB SUPPORT WORKS WITH 'django.contrib.sessions.backends.cache' ONLY
# ANOTHER SESSION STORE NEEDS DJANGO DEFAULT DATABASE ROUTER
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SERIALIZATION_MODULES = {
    'python' : 'keops.core.serializers.python',
    'json' : 'keops.core.serializers.json',
    'xml' : 'keops.core.serializers.xml_serializer',
    'yaml' : 'keops.core.serializers.pyyaml',
}

TEMPLATE_PROCESSORS = (
    "django.core.context_processors.request",
)

TEMPLATE_LOADERS = ['keops.template.loaders.app_directories.Loader',]

ROOT_URLCONF = 'keops.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
    '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s  %(module)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
